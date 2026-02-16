use async_openai::{Client, config::OpenAIConfig};
use clap::Parser;
use serde_json::{Value, json};
use std::{env, process};

#[derive(Parser)]
#[command(author, version, about)]
struct Args {
    #[arg(short = 'p', long)]
    prompt: String,
}

fn read(file_path: &str) -> std::io::Result<String> {
    std::fs::read_to_string(file_path)
}

fn write(file_path: &str, content: &str) -> std::io::Result<()> {
    std::fs::write(file_path, content)
}

fn bash(command: &str) -> std::io::Result<String> {
    let output = std::process::Command::new("sh")
        .arg("-c")
        .arg(command)
        .output()?;

    Ok(String::from_utf8_lossy(&output.stdout).to_string())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();

    let base_url = env::var("OPENROUTER_BASE_URL")
        .unwrap_or_else(|_| "https://openrouter.ai/api/v1".to_string());

    let api_key = env::var("OPENROUTER_API_KEY").unwrap_or_else(|_| {
        eprintln!("OPENROUTER_API_KEY is not set");
        process::exit(1);
    });

    let config = OpenAIConfig::new()
        .with_api_base(base_url)
        .with_api_key(api_key);

    let client = Client::with_config(config);

    let mut messages: Vec<Value> = Vec::new();

    messages.push(json!({
        "role": "user",
        "content": args.prompt,
    }));

    loop {
        #[allow(unused_variables)]
        let response: Value = client
            .chat()
            .create_byot(json!({
            "messages": messages,
            "model": "anthropic/claude-haiku-4.5",
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "read",
                        "description": "Reads a file from the filesystem",
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
                        "description": "Writes a file to the filesystem",
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
            ],
        }))
        .await?;

    let message = &response["choices"][0]["message"];

    if let Some(tool_calls_arr) = message["tool_calls"].as_array() {
        messages.push(message.clone());

        let tool_call = &tool_calls_arr[0];
        let id = tool_call["id"].as_str().unwrap();
        let name = tool_call["function"]["name"].as_str().unwrap();
        let arguments: Value =
            serde_json::from_str(tool_call["function"]["arguments"].as_str().unwrap())?;

        let result = if name == "read" {
            let file_path = arguments["file_path"].as_str().unwrap();
            read(file_path)?
        } else if name == "write" {
            let file_path = arguments["file_path"].as_str().unwrap();
            let content = arguments["content"].as_str().unwrap();
            write(file_path, content)?;
            "File written successfully".to_string()
        } else if name == "bash" {
            let command = arguments["command"].as_str().unwrap();
            bash(command)?
        } else {
            "Unknown tool".to_string()
        };

        messages.push(json!({
            "role": "tool",
            "tool_call_id": id,
            "content": result,
        }));
    } else if let Some(content) = message["content"].as_str() {
        println!("{}", content);
        break;
    }
    }

    Ok(())
}
