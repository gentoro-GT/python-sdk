from typing import List, Optional, Dict
from enum import Enum
import requests
import json


class Providers(str, Enum):
    OPENAI = 'openai'
    ANTHROPIC = 'anthropic'
    OPENAI_ASSISTANTS = 'openai_assistants'
    VERCEL = 'vercel'
    GENTORO = 'gentoro'


class AuthenticationScope(str, Enum):
    METADATA = 'metadata'
    API_KEY = 'api_key'


class Authentication:
    def __init__(self, scope: AuthenticationScope, metadata: Optional[Dict] = None):
        self.scope = scope
        self.metadata = metadata


class SdkConfig:
    def __init__(self, base_url: str, auth_mod_base_url: str, api_key: str, provider: Providers,
                 authentication: Authentication):
        if not api_key:
            raise ValueError("The api_key client option must be set")
        if not auth_mod_base_url:
            raise ValueError("Authentication module base URL is required")

        self.base_url = base_url
        self.auth_mod_base_url = auth_mod_base_url
        self.api_key = api_key
        self.provider = provider
        self.authentication = authentication


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
        self.auth_mod_uri = config.auth_mod_base_url
        self.authentication = config.authentication
        self.metadata = metadata or []
        self.auth_request_checker_id = None
        self.config = config

    def metadata(self, key: str, value: str):
        self.metadata.append({"key": key, "value": value})
        return self

    def get_tools(self, bridge_uid: str, messages: Optional[List[Dict]] = None):
        try:
            request_uri = f"/api/bornio/v1/inference/{bridge_uid}/retrievetools"

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


    def run_tools(self, bridge_uid: str, messages: Optional[List[Dict]], tool_calls: List[Dict]):
        try:
            request_uri = f"/api/bornio/v1/inference/{bridge_uid}/runtools"

            headers = {
                "X-API-Key": self.config.api_key,
                "Accept": "application/json",
                "User-Agent": "Python-SDK"
            }

            for tool_call in tool_calls:
                if "details" in tool_call and "arguments" in tool_call["details"]:
                    tool_call["details"]["arguments"] = json.dumps(tool_call["details"].get("arguments", {}))

            request_content = {
                "context": {"bridgeUid": bridge_uid, "messages": messages or []},
                "metadata": self.metadata,
                "authentication": {
                    "scope": self.authentication.scope.value,
                    "metadata": self.authentication.metadata if self.authentication.metadata else None
                },
                "toolCalls": tool_calls
            }

            result = self.transport.send_request(request_uri, request_content, headers=headers, method="POST")

            if result and "results" in result:
                return result["results"]
            return None
        except Exception as e:
            print(f"Error running tools: {e}")
            return None


    def add_event_listener(self, event_type: str, handler):
        try:
            print(f"Adding event listener for {event_type}")
        except Exception as e:
            print(f"Error adding event listener: {e}")