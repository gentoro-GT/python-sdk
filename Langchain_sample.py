import os
from Gentoro import Gentoro, SdkConfig, Providers
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage, HumanMessage

load_dotenv()
# Initialize the Gentoro and OpenAI instances
_gentoro = Gentoro(SdkConfig(provider=Providers.LANGCHAIN))
def filter_valid_messages(messages):
    valid_messages = []
    for msg in messages:
        if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
            valid_messages.append(msg)
        elif isinstance(msg, (AIMessage, ToolMessage)):
            valid_messages.append(msg)
    return valid_messages


# Initial messages to OpenAI
messages = [{"role": "user", "content": "what is the weather in nyc?"}]

tool = _gentoro.get_tools(os.getenv("GENTORO_BRIDGE_UID"), messages)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

llm_tools = llm.bind_tools(tool)
openai_response = llm_tools.invoke([msg.model_dump() if isinstance(msg, (AIMessage, SystemMessage, ToolMessage, HumanMessage)) else msg for msg in messages])
messages += [openai_response]


tool_calls = getattr(openai_response, "tool_calls", [])
if tool_calls:
    messages += _gentoro.run_tools(os.getenv("GENTORO_BRIDGE_UID"), messages, tool_calls=tool_calls)
else:
    print(llm_tools.invoke(messages))


messages = filter_valid_messages(messages)
response = llm_tools.invoke(messages)
print(response.content)