# Gentoro Python SDK

## Overview
Welcome to the **Gentoro Python SDK** documentation. This guide will help you integrate and use the SDK in your project.

## Supported Python Versions
This SDK is compatible with **Python >= 3.7**.

## Installation
To get started with the SDK, install it using **pip**:

```bash
pip install Gentoro==0.1.6
```

## Authentication
The Gentoro API uses an **API Key (`X-API-Key`)** for authentication. You must provide this key when making API requests.

To obtain an API Key, register at **Gentoro's API Portal**.

### Setting the API Key
When initializing the SDK, provide the configuration as follows:

```python
import os
from dotenv import load_dotenv
from Gentoro import Gentoro, SdkConfig, Providers

# Load environment variables
load_dotenv()

# Initialize SDK configuration
config = SdkConfig(
    base_url=os.getenv("GENTORO_BASE_URL"),
    api_key=os.getenv("GENTORO_API_KEY"),
    provider=Providers.OPENAI,
)

# Create an instance of the SDK
gentoro_instance = Gentoro(config)
bridge_uid = os.getenv("GENTORO_BRIDGE_UID")

# Fetch available tools
def get_tools():
    tools = gentoro_instance.get_tools(bridge_uid)
    print("Available tools:", tools)
    return tools

# Run a tool
def run_tool():
    tool_calls = [
        {
            "id": "1",
            "type": "function",
            "details": {
                "name": "say_hi",
                "arguments": {"name": "User_name"}
            }
        }
    ]
    result = gentoro_instance.run_tools(bridge_uid, messages=[], tool_calls=tool_calls)
    print("Tool execution result:", result)
    return result
if __name__ == "__main__":
    print("Fetching available tools...")
    get_tools()
    
    print("\nExecuting tool...")
    run_tool()
    
```

## SDK Services
### Methods
#### `get_tools(bridge_uid: str, messages: Optional[List[Dict]] = None) -> List[Dict]`
Fetches available tools for a specific `bridge_uid`.

Example usage:
```python
tools = gentoro_instance.get_tools("BRIDGE_ID", messages=[])
print("Tools:", tools)
```

#### `run_tools(bridge_uid: str, messages: List[Dict], tool_calls: List[Dict]) -> List[Dict]`
Executes the tools requested by the AI model.

Example usage:
```python
execution_result = gentoro_instance.run_tools("BRIDGE_ID", messages=[], tool_calls=tool_calls)
print("Execution Result:", execution_result)
```

## Providers
A provider defines how the SDK should handle and generate content:

```python
class Providers(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENAI_ASSISTANTS = "openai_assistants"
    VERCEL = "vercel"
    GENTORO = "gentoro"
```

## License
This SDK is licensed under the **Apache-2.0 License**. See the `LICENSE` file for more details.


