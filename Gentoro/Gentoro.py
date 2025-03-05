from typing import List, Optional, Dict, Union
from enum import Enum
import requests
import json
from .GentoroTypes import Providers, ExecResultType, BaseObject, ScopeForMetadata, Request, Response, Message,Context, KeyValuePair, GetToolsRequest, FunctionParameter, FunctionParameterCollection, Function, ToolDef, GetToolsResponse, TextContent, DataType, DataValue, ArrayContent, ObjectContent, FunctionCall, ToolCall, RunToolsRequest, ExecResultType, ExecOutput, ExecError, AuthSchemaField, AuthSchema, ExecResult, RunToolsResponse, SdkError, SdkEventType, SdkEvent
from openai.types.chat import ChatCompletion, ChatCompletionToolMessageParam, ChatCompletionContentPartTextParam, ChatCompletionMessage
import os

class AuthenticationScope(str, Enum):
    METADATA = 'metadata'
    API_KEY = 'api_key'


class Authentication:
    def __init__(self, scope: AuthenticationScope, metadata: Optional[Dict] = None):
        self.scope = scope
        self.metadata = metadata


class SdkConfig:
    def __init__(self, base_url: str = None, api_key: str = None, provider: Providers = Providers.GENTORO):
        # If base_url or api_key is not provided, try to get them from the environment
        if not base_url:
            base_url = os.getenv("GENTORO_BASE_URL")
        if not api_key:
            api_key = os.getenv("GENTORO_API_KEY")

        if not api_key:
            raise ValueError("The api_key client option must be set")

        self.base_url = base_url
        self.api_key = api_key
        self.provider = provider


class Transport:
    def __init__(self, config: SdkConfig):
        self.config = config

    def send_request(self, uri: str, content: Dict, method: str = "POST", headers: Dict = None):
        url = f"{self.config.base_url}{uri}"

        if headers is None:
            headers = {
                "X-API-Key": self.config.api_key,
                "Accept": "application/json"
            }

        try:
            if method.upper() == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            else:
                response = requests.post(url, json=content, headers=headers, timeout=10)

            response.raise_for_status()
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return None


class Gentoro:
    def __init__(self, config: SdkConfig, metadata: List[Dict] = None):
        self.transport = Transport(config)
        self.metadata = metadata or []
        self.auth_request_checker_id = None
        self.config = config

    def metadata(self, key: str, value: str):
        self.metadata.append({"key": key, "value": value})
        return self

    def get_tools(self, bridge_uid: str, messages: Optional[List[Dict]] = None):
        try:
            request_uri = f"/bornio/v1/inference/{bridge_uid}/retrievetools"

            headers = {
                "X-API-Key": self.config.api_key,
                "Accept": "application/json",
                "User-Agent": "Python-SDK"
            }

            request_content = {
                "context": {"bridgeUid": bridge_uid, "messages": messages or []},
                "metadata": self.metadata
            }

            result = self.transport.send_request(request_uri, request_content, headers=headers, method="POST")

            if result and "tools" in result:
                return self._as_provider_tools(result["tools"])
            return None
        except Exception as e:
            print(f"Error fetching tools: {e}")
            return None

    def _as_provider_tools(self, tools: List[Dict]) -> List[Dict]:
        if self.config.provider == Providers.OPENAI:
            return [
                {
                    "type": "function",
                    "function": {
                        "name": tool["definition"]["name"],
                        "description": tool["definition"]["description"],
                        "parameters": {
                            "type": "object",
                            "properties": {
                                param["name"]: {"type": param["type"], "description": param["description"]}
                                for param in tool["definition"]["parameters"].get("properties", [])
                            },
                            "required": tool["definition"]["parameters"].get("required", []),
                        },
                    },
                }
                for tool in tools
            ]
        return tools

    def as_internal_tool_calls(self, messages: Dict) -> Optional[List[Dict]]:
        """
        Extracts tool calls from OpenAI and Gentoro responses.
        """
        if self.config.provider == Providers.OPENAI:
            if isinstance(messages, ChatCompletion):
                response_choice = messages.choices[0]
                response_message = response_choice.message
                if response_choice.finish_reason == "tool_calls" and response_message.tool_calls:
                    tool_calls = response_message.tool_calls
                    if not tool_calls:
                        return []

                    return [
                        {
                            "id": call.id,
                            "type": call.type,
                            "details": {
                                "name": call.function.name,
                                "arguments": call.function.arguments
                            }
                        }
                        for call in tool_calls  # Corrected iteration over tool_calls
                    ]
            else:
                return messages  # Removed unnecessary result variable
        elif self.config.provider == Providers.GENTORO:
            return messages if isinstance(messages, list) else []

        return None


    def run_tool_natively(self, bridge_uid: str, tool_name: str, params: Optional[Dict] = None):
        """
        Executes a tool natively by directly calling runTools with the specified tool.
        """
        request_content = {
            "id": "native",
            "type": "function",
            "details": {
                "name": tool_name,
                "arguments": json.dumps(params) if params is not None else "{}"
            }
        }

        try:
            result = self.run_tools(bridge_uid, None, [request_content])
            return result[0] if result else None
        except Exception as e:
            print(f"Error running tool natively: {e}")
            return None


    def run_tools(self, bridge_uid: str, messages: Optional[List[Dict]], tool_calls: Union[List[Dict], ChatCompletion]):
        try:
            request_uri = f"/bornio/v1/inference/{bridge_uid}/runtools"

            headers = {
                "X-API-Key": self.config.api_key,
                "Accept": "application/json",
                "User-Agent": "Python-SDK"
            }
            _tool_calls = tool_calls
            if isinstance(tool_calls, ChatCompletion):
                extracted_tool_calls = self.as_internal_tool_calls(tool_calls)
                if extracted_tool_calls is None:
                    print("No valid tool calls extracted from OpenAI response.")
                    return None
                tool_calls = extracted_tool_calls
            elif not isinstance(tool_calls, ChatCompletion):
                extracted_tool_calls = self.as_internal_tool_calls(tool_calls)
            if extracted_tool_calls:
                if not isinstance(tool_calls, list):
                    tool_calls = list(tool_calls) if tool_calls else []
                tool_calls.extend(extracted_tool_calls)

            filtered_tool_calls = []

            for tool_call in tool_calls:
                if isinstance(tool_call, dict) and "details" in tool_call and isinstance(tool_call["details"], dict):
                    # Ensure arguments exist and are in dictionary format before serializing
                    if "arguments" in tool_call["details"]:
                        if isinstance(tool_call["details"]["arguments"], dict):
                            tool_call["details"]["arguments"] = json.dumps(
                                tool_call["details"]["arguments"])

                    filtered_tool_calls.append(tool_call)
            tool_calls = filtered_tool_calls
            # Validate message sequence before sending request
            # Ensure assistant message with tool_calls exists
            if not messages or not any("tool_calls" in msg for msg in messages if isinstance(msg, dict)):
                if isinstance(tool_calls, list) and tool_calls:
                    # Ensure tool_calls are correctly structured
                    corrected_tool_calls = [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["details"]["name"],
                                "arguments": tc["details"]["arguments"]
                            }
                        }
                        for tc in tool_calls
                    ]

                    assistant_message = {
                        "role": "assistant",
                        "content": None,
                        "tool_calls": corrected_tool_calls
                    }

            # Prepare request payload
            request_content = {
                "context": {"bridgeUid": bridge_uid, "messages": messages},
                "metadata": self.metadata,
                "toolCalls": tool_calls
            }

            # Send request
            result = self.transport.send_request(request_uri, request_content, headers=headers, method="POST")
            if result is None:
                print("Error: API response is None.")
                return []

            return self.as_provider_tool_call_results(_tool_calls, result)

            result = self.transport.send_request(request_uri, request_content, headers=headers, method="POST")
            return self.as_provider_tool_call_results(_tool_calls, result)
            # if result and "results" in result:
            #     return result["results"]
            # return None
        except Exception as e:
            print(f"Error running tools: {e},tool_calls:{tool_calls}")
            return None

    def as_provider_tool_call_results(self, tool_calls: Union[List[Dict], ChatCompletion], results: Dict) -> Union[
        List[Dict], List[ChatCompletionToolMessageParam]]:
        """
        Build tool call results from OpenAI and Gentoro responses.
        """
        messages = []

        if self.config.provider == Providers.OPENAI:
            if isinstance(tool_calls, ChatCompletion):
                converted_message = self.convert_message_to_dict(tool_calls.choices[0].message)

                # Avoid duplicate assistant messages
                if not any(msg.get("role") == "assistant" and "tool_calls" in msg for msg in messages):
                    messages.append(converted_message)

            for result in results["results"]:
                if result["type"] == ExecResultType.EXEC_OUTPUT:
                    # Prevent duplicate tool responses
                    if not any(
                            msg["role"] == "tool" and msg["tool_call_id"] == result["toolCallId"] for msg in messages):
                        messages.append(ChatCompletionToolMessageParam(
                            role="tool",
                            tool_call_id=result["toolCallId"],
                            content=result["data"]["content"]
                        ))
                elif result["type"] == ExecResultType.ERROR:
                    messages.append(ChatCompletionToolMessageParam(
                        role="tool",
                        tool_call_id=result["toolCallId"],
                        content=f"Failed while attempting to execute tool:\n```{result['data']['message']}```"
                    ))
                else:
                    raise ValueError(f"Unknown result type: {result['type']}")

        elif self.config.provider == Providers.GENTORO:
            if isinstance(tool_calls, list):
                messages.extend(tool_calls)
            messages.extend(results["results"])

        return messages

    def convert_message_to_dict(self, message: ChatCompletionMessage) -> Dict:
        """Converts a ChatCompletionMessage object to a dictionary format."""
        return {
            "role": message.role,
            "content": message.content,
            "function_call": message.function_call if message.function_call else None,
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": json.dumps(json.loads(tool_call.function.arguments))
                    }
                }
                for tool_call in message.tool_calls
            ] if message.tool_calls else None
        }

    def add_event_listener(self, event_type: str, handler):
        try:
            print(f"Adding event listener for {event_type}")
        except Exception as e:
            print(f"Error adding event listener: {e}")
