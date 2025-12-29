"""Weather agent using Pydantic AI with BatchTool for parallel execution."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from pydantic_ai import Agent

from rayai import agent

load_dotenv(Path(__file__).parent.parent.parent / ".env")

REQUIRED_KEYS = ["OPENAI_API_KEY", "WEATHER_API_KEY"]
missing = [k for k in REQUIRED_KEYS if not os.environ.get(k)]
if missing:
    sys.exit(f"Missing required environment variables: {', '.join(missing)}")

from .tools import batch_weather  # noqa: E402

SYSTEM_PROMPT = """\
You are a helpful weather assistant.

When users ask about weather in one or more cities, use the batch tool to fetch
weather data for all cities in parallel. This is much faster than fetching them
one at a time.

To use the batch tool, call it with:
- tool_name: "get_weather"
- tool_inputs: a list of dicts, each with a "city" key

Example: To get weather for NYC, London, and Tokyo:
tool_name="get_weather"
tool_inputs=[{"city": "New York"}, {"city": "London"}, {"city": "Tokyo"}]

After receiving the weather data, provide a friendly summary to the user.
"""


@agent(num_cpus=1, memory="1GB")
class Weather:
    """Weather agent with BatchTool for parallel city weather fetching."""

    def __init__(self):
        self.pydantic_agent = Agent(
            "openai:gpt-4o-mini",
            system_prompt=SYSTEM_PROMPT,
            tools=[batch_weather],
        )

    async def run(self, data: dict) -> dict:
        """Execute the weather agent.

        Args:
            data: Input data in OpenAI Chat API format

        Returns:
            Dict with 'response' key containing agent output
        """
        messages = data.get("messages", [])
        if not messages:
            return {"error": "No messages provided"}

        user_message = None
        for msg in reversed(messages):
            if msg.get("role") == "user":
                user_message = msg.get("content", "")
                break

        if not user_message:
            return {"error": "No user message found"}

        result = await self.pydantic_agent.run(user_message)
        return {"response": result.output}
