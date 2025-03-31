import os
from Gentoro import Gentoro, SdkConfig, Providers
from dotenv import load_dotenv
import openai

# Load environment variables from .env file
load_dotenv()


# Initialize the Gentoro and OpenAI instances
_gentoro = Gentoro(SdkConfig(provider=Providers.OPENAI))
_openAI = openai.OpenAI()

# Define the OpenAI model we want to use
MODEL = 'gpt-4o-mini'

# Initial messages to OpenAI
messages = [{"role": "user", "content": "how is the weather in new york?"}]

# Send message, along with available tools to OpenAI
openai_response = _openAI.chat.completions.create(
    model=MODEL,
    messages=messages,
    tools=_gentoro.get_tools(os.getenv("GENTORO_BRIDGE_UID"), messages)
)
messages += _gentoro.run_tools(os.getenv("GENTORO_BRIDGE_UID"), messages, openai_response)

# Continue with communication with OpenAI
response = _openAI.chat.completions.create(
  model=MODEL,
  messages=messages,
  tools=_gentoro.get_tools(os.getenv("GENTORO_BRIDGE_UID"), messages)
)

# Prints the response with the answer
print("final response",response.choices[0].message.content)