import argparse
import os
import sys
import json
import subprocess

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")



def call_model(messages, tools):
    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    response = client.chat.completions.create(
        # model="stepfun/step-3.5-flash:free",
        model="anthropic/claude-haiku-4.5",
        messages=messages,
        tools=tools
    )
    return response

def read(file_path: str) -> str:
    with open(file_path, "r") as f:
        return f.read()
    
def write(file_path: str, content: str) -> str:
    os.makedirs(os.path.dirname(file_path), exist_ok=True) 
    with open(file_path, "w") as f:
        f.write(content)
    return f"Successfully wrote to {file_path}"   

def bash(command: str) -> str:
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

TOOLS = {"read": read, "write": write, "bash": bash}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    messages=[{"role": "user", "content": args.p}]
    tools=[{
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
                    "required": ["file_path", "content"],
                    "properties": {
                        "file_path": {
                            "type": "string",
                            "description": "The path to the file to read"
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
                    "required": ["command"],
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

    while True:

        chat = call_model(messages, tools)

        if not chat.choices or len(chat.choices) == 0:
            raise RuntimeError("no choices in response")
        
        message = chat.choices[0].message
        messages.append(message)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                fn = tool_call.function
                function = fn.name
                fn_args = json.loads(fn.arguments)
                messages.append(
                    {"role": "tool", "tool_call_id": tool_call.id, "content": TOOLS[function](**fn_args)}
                )

        if chat.choices[0].finish_reason == "stop":
            break
    
    print(chat.choices[0].message.content)

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)


if __name__ == "__main__":
    main()
