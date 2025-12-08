"""
Example ChatGPT Plus client using the chat2api proxy.

Usage:
    CHATGPT_ACCESS_TOKEN="your_access_token" \
    CHAT2API_BASE_URL="http://127.0.0.1:5005" \
    python examples/chatgpt_plus_chat.py "اكتب لي نكتة قصيرة"

Environment variables:
    CHATGPT_ACCESS_TOKEN: AccessToken or RefreshToken for your ChatGPT Plus account.
    CHAT2API_BASE_URL: chat2api base URL (default: http://127.0.0.1:5005).
    CHATGPT_MODEL: Model name to request (default: gpt-4o).
"""

import json
import os
import sys
from typing import Iterable

import requests


def stream_chat(prompt: str) -> None:
    base_url = os.getenv("CHAT2API_BASE_URL", "http://127.0.0.1:5005").rstrip("/")
    token = os.getenv("CHATGPT_ACCESS_TOKEN")
    model = os.getenv("CHATGPT_MODEL", "gpt-4o")

    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt},
        ],
        "stream": True,
    }

    response = requests.post(
        f"{base_url}/v1/chat/completions",
        headers=headers,
        json=payload,
        stream=True,
        timeout=60,
    )
    response.raise_for_status()

    for delta in iter_deltas(response):
        print(delta, end="", flush=True)
    print()


def iter_deltas(response: requests.Response) -> Iterable[str]:
    for line in response.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        if line.strip() == "data: [DONE]":
            break

        data = json.loads(line[6:])
        delta = data["choices"][0]["delta"].get("content")
        if delta:
            yield delta


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit("Usage: python examples/chatgpt_plus_chat.py '<your prompt>'")
    prompt = sys.argv[1]
    stream_chat(prompt)


if __name__ == "__main__":
    main()
