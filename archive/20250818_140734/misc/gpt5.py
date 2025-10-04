#!/usr/bin/env python3
"""
Direct GPT-5 query tool - bypasses LlamaIndex validation
Usage: poetry run python gpt5.py "your question"
"""

import os
import sys

from openai import OpenAI

# Get the question from command line
if len(sys.argv) < 2:
    print("Usage: poetry run python gpt5.py 'your question'")
    sys.exit(1)

question = " ".join(sys.argv[1:])

# Load API key from .env
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Direct GPT-5 call
try:
    response = client.chat.completions.create(
        model="gpt-5", messages=[{"role": "user", "content": question}]
    )

    print(response.choices[0].message.content)

except Exception as e:
    print(f"Error: {e}")
