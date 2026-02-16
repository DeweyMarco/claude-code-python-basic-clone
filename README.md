# Build Your Own Claude Code (Python)

A minimal implementation of an LLM-powered coding assistant, similar to Claude Code.

## Overview

This project demonstrates how to build an AI coding assistant that can:
- Read and write files
- Execute shell commands
- Use an **agent loop** to iteratively solve tasks

## Key Concepts

### Agent Loop
The core pattern is an **agent loop** where the LLM repeatedly:
1. Receives a user prompt and conversation history
2. Decides whether to call a tool or respond directly
3. If a tool is called, the result is added to the conversation
4. Loop continues until the LLM responds without tool calls

### Tool Calling
Tools are functions the LLM can invoke. Each tool has:
- A **name** and **description** for the LLM to understand its purpose
- A **JSON schema** defining the expected parameters
- A **Python function** that executes the actual logic

## Project Structure

```
app/
  main.py    # Main entry point with agent loop and tool definitions
```

## Setup

1. Install dependencies with `uv`:
   ```sh
   uv sync
   ```

2. Set your API key in a `.env` file:
   ```
   OPENROUTER_API_KEY=your_key_here
   ```

3. Run the assistant:
   ```sh
   ./your_program.sh -p "Your prompt here"
   ```

## How It Works

See `app/main.py` for the complete implementation with inline comments explaining each part.
