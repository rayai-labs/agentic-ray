# CLAUDE.md

## Purpose of This Directory

This example demonstrates **BatchTool** - a feature that enables parallel execution of tool calls via Ray. The weather agent shows how an LLM can decide what arguments to pass to a batch operation, fetching weather for multiple cities simultaneously.

## Directory Structure

```
weather_agent/
├── agents/
│   └── weather/
│       ├── agent.py    # Weather agent with LLM-driven batching
│       └── tools.py    # get_weather tool + BatchTool wrapper
├── .env.example        # Required API keys
├── pyproject.toml      # Dependencies
├── README.md           # Usage documentation
└── CLAUDE.md           # This file
```

## Key Concepts

### BatchTool Pattern

1. **Single Tool**: `get_weather(city)` fetches weather for ONE city
2. **BatchTool Wrapper**: `batch_weather = BatchTool(tools=[get_weather])`
3. **Batch Call**: `batch_weather("get_weather", [{"city": "NYC"}, {"city": "London"}])`
4. **Parallel Execution**: Ray executes all inputs simultaneously

### OpenAI Tool Calling + BatchTool

The agent uses OpenAI's function/tool calling feature:
1. Define tool schema with `cities` array parameter
2. LLM decides when to call the tool and with what cities
3. Agent executes BatchTool with LLM's chosen arguments
4. Tool result sent back to LLM for final response

This demonstrates true agentic behavior where the LLM controls tool invocation.

## Architecture Flow

```
User Query
    │
    ▼
┌──────────────────────────────────────┐
│ LLM with tools=[get_weather_batch]   │
│                                      │
│ LLM decides to call:                 │
│ get_weather_batch(cities=["NYC",...])│
└──────────────────────────────────────┘
    │
    ▼
┌──────────────────────┐
│ BatchTool: Parallel  │  → 3 simultaneous API calls
│ get_weather() calls  │
└──────────────────────┘
    │
    ▼
┌──────────────────────┐
│ Tool result → LLM    │  → LLM generates response
└──────────────────────┘
```

## Key Files

- **tools.py**: Defines `get_weather` tool and wraps it with `BatchTool`
- **agent.py**: `Weather` agent class that orchestrates LLM + BatchTool

## Required Environment Variables

- `OPENAI_API_KEY`: For LLM calls (city extraction, summarization)
- `WEATHER_API_KEY`: OpenWeatherMap API key

## Do / Don't

### Do:
- Use this as a template for other batch operations (stocks, files, APIs)
- Follow the pattern: single tool → BatchTool wrapper → LLM decides args
- Handle errors gracefully (BatchTool provides per-item error tracking)

### Don't:
- Hardcode the batch inputs (let the LLM decide)
- Skip error handling in batch results
- Use this for operations that must be sequential

## Related Modules

- `src/rayai/batch.py` - BatchTool implementation
- `src/rayai/decorators.py` - `@tool` decorator
- `examples/finance_agent/` - Another example using tools
