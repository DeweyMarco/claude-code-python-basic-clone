"""
Claude Code Clone - A minimal LLM-powered coding assistant.

This implementation demonstrates the core "agent loop" pattern used by AI coding
assistants. The LLM iteratively calls tools until it has enough information to
respond to the user.
"""

import argparse
import os
import sys
import json
import subprocess

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# Configuration for OpenRouter API (OpenAI-compatible endpoint)
API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")



def call_model(messages, tools):
    """
    Send a request to the LLM with conversation history and available tools.

    Args:
        messages: List of conversation messages (user, assistant, tool results)
        tools: List of tool definitions the LLM can choose to call

    Returns:
        The API response containing the LLM's reply (text and/or tool calls)
    """
    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    response = client.chat.completions.create(
        model="anthropic/claude-haiku-4.5",
        messages=messages,
        tools=tools
    )
    return response

# =============================================================================
# TOOL IMPLEMENTATIONS
# These are the actual functions that get executed when the LLM calls a tool.
# =============================================================================

def read(file_path: str) -> str:
    """Read and return the contents of a file."""
    with open(file_path, "r") as f:
        return f.read()


def write(file_path: str, content: str) -> str:
    """Write content to a file, creating directories if needed."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "w") as f:
        f.write(content)
    return f"Successfully wrote to {file_path}"


def bash(command: str) -> str:
    """Execute a shell command and return stdout."""
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout


# Map tool names to their implementations for easy lookup
TOOLS = {"read": read, "write": write, "bash": bash}

def main():
    # Parse command line arguments
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True, help="The prompt to send to the assistant")
    args = p.parse_args()

    # Initialize conversation with the user's prompt
    messages = [{"role": "user", "content": args.p}]

    # ==========================================================================
    # TOOL DEFINITIONS (JSON Schema)
    # These tell the LLM what tools are available and how to call them.
    # The LLM uses these descriptions to decide when and how to use each tool.
    # ==========================================================================
    tools = [
        {
            "type": "function",
            "function": {
                "name": "read",
                "description": "Read and return the contents of a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to read"
                        }
                    },
                    "required": ["file_path"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "write",
                "description": "Write the contents to a file",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file"
                        }
                    },
                    "required": ["file_path", "content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "bash",
                "description": "Execute a shell command",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The shell command to execute"
                        }
                    },
                    "required": ["command"]
                }
            }
        }
    ]

    # ==========================================================================
    # AGENT LOOP
    # This is the core pattern: repeatedly call the LLM until it stops.
    # Each iteration, the LLM either:
    #   1. Calls one or more tools (we execute them and continue)
    #   2. Responds with text and finish_reason="stop" (we exit the loop)
    # ==========================================================================
    while True:
        # Send current conversation to the LLM
        chat = call_model(messages, tools)

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")

        # Add the assistant's response to conversation history
        message = chat.choices[0].message
        messages.append(message)

        # If the LLM requested tool calls, execute them
        if message.tool_calls:
            for tool_call in message.tool_calls:
                # Parse the tool call
                fn = tool_call.function
                function_name = fn.name
                fn_args = json.loads(fn.arguments)

                # Execute the tool and add result to conversation
                result = TOOLS[function_name](**fn_args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result
                })

        # Exit loop when the LLM is done (no more tool calls)
        if chat.choices[0].finish_reason == "stop":
            break

    # Print the final response to the user
    print(chat.choices[0].message.content)

    # Debug logging (visible in test output)
    print("Logs from your program will appear here!", file=sys.stderr)


if __name__ == "__main__":
    main()
