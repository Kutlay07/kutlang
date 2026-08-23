from openai import OpenAI


MODEL = (
    r".\models\gguf\Qwen2.5-Coder-14B-Instruct-Q4_K_M"
    r"\qwen2.5-coder-14b-instruct-q4_k_m.gguf"
)

client = OpenAI(
    base_url="http://localhost:8080/v1",
    api_key="not-needed",
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to the file to read.",
                    }
                },
                "required": ["path"],
            },
        },
    }
]


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


messages = [
    {
        "role": "user",
        "content": "Read the file main.py and tell me what it does.",
    }
]

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {
            "role": "user",
            "content": "Read the file main.py.",
        }
    ],
    tools=tools,
    max_tokens=64,
    temperature=0,
)

message = response.choices[0].message

print("ASSISTANT:")
print(message.content)

print("\nTOOL CALLS:")
print(message.tool_calls)


if message.tool_calls:
    tool_call = message.tool_calls[0]

    print("\nEXECUTING TOOL:")
    print(tool_call.function.name)
    print(tool_call.function.arguments)

    import json

    arguments = json.loads(tool_call.function.arguments)

    result = read_file(arguments["path"])

    messages.append(message)

    messages.append(
        {
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": result,
        }
    )

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": "Read the file main.py.",
            }
        ],
        tools=tools,
        max_tokens=64,
        temperature=0,
    )

    print("\nFINAL RESPONSE:")
    print(response.choices[0].message.content)