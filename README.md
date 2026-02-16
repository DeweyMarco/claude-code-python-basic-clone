# Build Your Own Claude Code

A minimal implementation of an LLM-powered coding assistant, similar to Claude Code. Available in both **Python** and **Rust**.

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
- An implementation function that executes the actual logic

## Project Structure

```
app/
  main.py        # Python implementation
rust/
  src/main.rs    # Rust implementation
  Cargo.toml     # Rust dependencies
```

## Setup

### Python

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

### Rust

1. Build the project:
   ```sh
   cd rust
   cargo build --release
   ```

2. Set your API key:
   ```sh
   export OPENROUTER_API_KEY=your_key_here
   ```

3. Run the assistant:
   ```sh
   ./target/release/codecrafters-claude-code -p "Your prompt here"
   ```

## How It Works

Both implementations follow the same pattern:

1. **Parse CLI arguments** - Accept a prompt via `-p` flag
2. **Initialize conversation** - Create a messages array with the user prompt
3. **Define tools** - Specify available tools (read, write, bash) with JSON schemas
4. **Agent loop** - Repeatedly call the LLM until it responds without tool calls
5. **Execute tool calls** - When the LLM requests a tool, execute it and add results to conversation
6. **Output response** - Print the final LLM response

See `app/main.py` (Python) or `rust/src/main.rs` (Rust) for the complete implementation with inline comments.
