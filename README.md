# Gentoro Python SDK

## Overview
Welcome to the **Gentoro Python SDK** documentation. This guide will help you integrate and use the SDK in your project.

## Supported Python Versions
This SDK is compatible with **Python >= 3.7**.

## Installation
To get started with the SDK, install it using **pip**:

```bash
pip install -e .
```

## Authentication
The Gentoro API uses an **API Key (`X-API-Key`)** for authentication. You must provide this key when making API requests.

To obtain an API Key, register at **Gentoro's API Portal**.

### Setting the API Key
When initializing the SDK, provide the configuration as follows:

```python
from Gentoro import Gentoro, SdkConfig, Authentication, AuthenticationScope, Providers

config = SdkConfig(
    api_key="your_api_key_here",  # Your Gentoro API Key
    base_url="https://stage.gentoro.com",  # Base URL where the Gentoro API is hosted
    auth_mod_base_url="https://stage.gentoro.com/auth",  # Authentication module base URL
    provider=Providers.OPENAI,
    authentication=Authentication(scope=AuthenticationScope.API_KEY)
)

gentoro_instance = Gentoro(config)
bridge_uid = "BRIDGE_ID"  # Example bridge UID

# Fetch tools
tools = gentoro_instance.get_tools(bridge_uid)
print("Fetched tools:", tools)

# Execute a tool
tool_calls = [
    {
        "id": "tool_123",
        "type": "function",
        "details": {"name": "example_tool", "arguments": "{}"}
    }
]

execution_result = gentoro_instance.run_tools(bridge_uid, messages=[], tool_calls=tool_calls)
print("Execution result:", execution_result)
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


