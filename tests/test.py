import unittest
import os
from dotenv import load_dotenv
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))
from Gentoro.Gentoro import Gentoro, SdkConfig, Providers

# Load environment variables from the `.env` file inside the `tests/` folder
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)


class TestGentoroSDK(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Setup SDK configuration before running tests"""
        cls.config = SdkConfig(
            base_url=os.getenv("GENTORO_BASE_URL"),
            api_key=os.getenv("GENTORO_API_KEY"),
            provider=Providers.GENTORO,
        )

        cls.gro_instance = Gentoro(cls.config)
        cls.bridge_uid = os.getenv("GENTORO_BRIDGE_UID")


    def test_get_tools(self):
        """Test fetching available tools with dynamic bridge UID"""
        print("\nRunning get_tools test...")
        tools = self.gro_instance.get_tools(self.bridge_uid)

        self.assertIsNotNone(tools, "Failed to fetch tools")
        print("Fetched tools:", tools)


    def test_run_tools(self):
        """Test executing tools"""
        print("\nRunning run_tools test...")

        tool_calls = [
            {
                "id": "1",
                "type": "function",
                "details": {
                    "name": "say_hi",
                    "arguments": {"name": "Mohit"}
                }
            }
        ]

        result = self.gro_instance.run_tools(self.bridge_uid, messages=[], tool_calls=tool_calls)

        self.assertIsNotNone(result, "Failed to execute tools")
        print("Tool execution result:", result)

    def test_run_tool_natively(self):
        """Test executing a tool natively using run_tool_natively"""
        print("\nRunning run_tool_natively test...")

        tool_name = "say_hi"
        params = {"name": "Mohit"}
        result = self.gro_instance.run_tool_natively(self.bridge_uid, tool_name, params)

        self.assertIsNotNone(result, "Failed to execute tool natively")
        print("Native tool execution result:", result)


if __name__ == "__main__":
    unittest.main()
