# Weather Agent - BatchTool Example

This example demonstrates how to use **BatchTool** for parallel API execution with **OpenAI tool calling**. The LLM decides when to call the batch tool and with what arguments, then BatchTool fetches weather for multiple cities simultaneously via Ray.

## What This Demonstrates

- **OpenAI Tool Calling** - LLM decides when/how to call tools
- **BatchTool** - Wrap a single tool to enable parallel execution with multiple inputs
- **Parallel API Calls** - All weather API calls execute simultaneously via Ray

## How It Works

```
User: "What's the weather in NYC, London, and Tokyo?"
                    │
                    ▼
         ┌─────────────────────────────────────┐
         │  Step 1: LLM receives message       │
         │  LLM decides to call tool:          │
         │                                     │
         │  get_weather_batch(                 │
         │    cities=["NYC", "London", "Tokyo"]│
         │  )                                  │
         └─────────────────────────────────────┘
                    │
                    ▼
         ┌─────────────────────────────────────┐
         │  Step 2: BatchTool executes         │
         │  in parallel via Ray:               │
         │                                     │
         │  ┌─────┐  ┌────────┐  ┌───────┐    │
         │  │ NYC │  │ London │  │ Tokyo │    │
         │  └──┬──┘  └───┬────┘  └───┬───┘    │
         │     │         │           │        │
         │     ▼         ▼           ▼        │
         │   72°F      55°F        68°F       │
         └─────────────────────────────────────┘
                    │
                    ▼
         ┌─────────────────────────────────────┐
         │  Step 3: Tool result sent to LLM    │
         │  LLM generates friendly response    │
         └─────────────────────────────────────┘
```

## Setup

1. **Get API Keys:**
   - OpenAI API key from [OpenAI](https://platform.openai.com/)
   - Weather API key from [OpenWeatherMap](https://openweathermap.org/api) (free tier available)

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Install dependencies:**
   ```bash
   pip install -e .
   ```

## Run the Agent

```bash
cd examples/weather_agent
rayai serve
```

## Test the Agent

```bash
curl -X POST http://localhost:8000/agents/weather/chat \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "What is the weather in New York, London, Tokyo, and Sydney?"}
    ]
  }'
```

## Example Response

```json
{
  "response": "Here's the current weather:\n- New York: 72°F and sunny\n- London: 55°F and cloudy\n- Tokyo: 68°F and clear\n- Sydney: 77°F and humid",
  "cities_requested": ["New York", "London", "Tokyo", "Sydney"],
  "weather_data": [
    {"city": "New York", "temperature": 22, "condition": "clear sky", "humidity": 45},
    {"city": "London", "temperature": 13, "condition": "overcast clouds", "humidity": 78},
    {"city": "Tokyo", "temperature": 20, "condition": "few clouds", "humidity": 55},
    {"city": "Sydney", "temperature": 25, "condition": "scattered clouds", "humidity": 65}
  ],
  "status": "success"
}
```

## Key Code

### tools.py - Single tool wrapped with BatchTool

```python
@tool(desc="Get current weather for a city")
def get_weather(city: str) -> dict:
    # Fetch weather for ONE city
    ...

# Wrap with BatchTool for parallel execution
batch_weather = BatchTool(tools=[get_weather])
```

### agent.py - Pydantic AI with BatchTool

```python
from pydantic_ai import Agent
from .tools import batch_weather

# Pass BatchTool directly to Pydantic AI
self.pydantic_agent = Agent(
    "openai:gpt-4o-mini",
    system_prompt=SYSTEM_PROMPT,
    tools=[batch_weather],  # BatchTool is exposed as a tool
)

# LLM calls BatchTool with tool_name and tool_inputs
# batch_weather("get_weather", [{"city": "NYC"}, {"city": "London"}])
```

## Performance

- **Sequential:** 4 cities × 1s/request = 4 seconds
- **Parallel (BatchTool):** 4 cities in parallel = ~1 second

BatchTool leverages Ray's distributed execution to run all API calls simultaneously.
