from typing import List, Dict
import sys
import os

# Add the parent directory of `Gentoro` to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))

from Gentoro.Gentoro import Gentoro, SdkConfig, Authentication, AuthenticationScope, Providers  # Import from your SDK module

import unittest

class TestGentoroSDK(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup SDK configuration before running tests"""
        cls.config = SdkConfig(
            base_url="https://stage.gentoro.com",  # Updated base URL
            auth_mod_base_url="https://stage.gentoro.com/auth",  # Update if required
            api_key="ffab9d795347384aa9e20571436ff44c95beba518f311e12b67b278fa6d73ffb",  # Replace with a valid API key
            provider=Providers.OPENAI,  # Change as per requirement
            authentication=Authentication(scope=AuthenticationScope.API_KEY)
        )

        cls.gro_instance = Gentoro(cls.config)
        cls.bridge_uid = "7MuRXMmQUVru8IWJTLorCc"  # Example bridge UID

    def test_get_tools(self):
        """Test fetching available tools with dynamic bridge UID"""
        print("\nRunning get_tools test...")
        tools = self.gro_instance.get_tools(self.bridge_uid)

        self.assertIsNotNone(tools, "Failed to fetch tools")
        print("Fetched tools:", tools)

    def test_run_tools(self):
        """Test executing tools"""
        print("\nRunning run_tools test...")

        tool_calls = {
            "messages": [],
            "metadata": [],
            "toolCalls": [
                {
                    "id": "1",
                    "type": "function",
                    "details": {
                        "name": "say_hi",
                        "arguments": "{}"
                    }
                }
            ]
        }


        result = self.gro_instance.run_tools(self.bridge_uid, messages=[], tool_calls=tool_calls)

        self.assertIsNotNone(result, "Failed to execute tools")
        print("Tool execution result:", result)

if __name__ == "__main__":
    unittest.main()
