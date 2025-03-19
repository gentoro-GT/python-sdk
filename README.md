# Gentoro Python SDK

## Overview
Welcome to the **Gentoro Python SDK** documentation. This guide will help you integrate and use the SDK in your project.

## Supported Python Versions
This SDK is compatible with **Python >= 3.10**.

## Installation
To get started with the SDK, install it using **pip**:

```bash
pip install Gentoro==0.1.8
```

## Authentication
The Gentoro API uses an **API Key (`X-API-Key`)** for authentication. You must provide this key when making API requests.

To obtain an API Key, register at **Gentoro's API Portal**.

### Setting the API Key
When initializing the SDK, provide the configuration as follows:

```python
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
messages = [{"role": "user", "content": "list 10 of my slack channels"}]

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
    
```

## SDK Services
### Methods
#### `get_tools(bridge_uid: str, messages: Optional[List[Dict]] = None) -> List[Dict]`
Fetches available tools for a specific `bridge_uid`.

Example usage:
```python
tools = _gentoro.get_tools("BRIDGE_ID", messages=[])
print("Tools:", tools)
```

#### `run_tools(bridge_uid: str, messages: List[Dict], tool_calls: List[Dict]) -> List[Dict]`
Executes the tools requested by the AI model.

Example usage:
```python
execution_result = _gentoro.run_tools("BRIDGE_ID", messages=[], tool_calls=tool_calls)
print("Execution Result:", execution_result)
```

## Providers
A provider defines how the SDK should handle and generate content:


## License
This SDK is licensed under the **Apache-2.0 License**. See the `LICENSE` file for more details.


