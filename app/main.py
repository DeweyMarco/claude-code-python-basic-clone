import argparse
import os
import sys
import json

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL", default="https://openrouter.ai/api/v1")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("-p", required=True)
    args = p.parse_args()

    if not API_KEY:
        raise RuntimeError("OPENROUTER_API_KEY is not set")

    client = OpenAI(api_key=API_KEY, base_url=BASE_URL)

    chat = client.chat.completions.create(
        model="stepfun/step-3.5-flash:free",
        messages=[{"role": "user", "content": args.p}],
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
                }}]
    )

    if not chat.choices or len(chat.choices) == 0:
        raise RuntimeError("no choices in response")
    
    if chat.choices[0].message.tool_calls:
        for tool_call in chat.choices[0].message.tool_calls:
            if tool_call.function.name == "read":
                func_args = json.loads(tool_call.function.arguments)
                file_path = func_args["file_path"]
                with open(file_path, "r") as f:
                    content = f.read()
                print(content)

    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!", file=sys.stderr)

    # TODO: Uncomment the following line to pass the first stage
    print(chat.choices[0].message.content)


if __name__ == "__main__":
    main()
