import os

from dotenv import load_dotenv
from groq import Groq


# Load environment variables from .env
load_dotenv()


# Get Groq API key
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError(
        "GROQ_API_KEY was not found. "
        "Please add it to your .env file."
    )


# Create Groq client
client = Groq(api_key=api_key)


def generate_response(messages):
    """
    Send a conversation to Groq and return the AI response.
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content


if __name__ == "__main__":

    messages = [
        {
            "role": "system",
            "content": (
                "You are a professional technical interviewer. "
                "Be concise and conversational."
            )
        },
        {
            "role": "user",
            "content": "What is a vector database?"
        }
    ]

    answer = generate_response(messages)

    print("\nGroq Response:")
    print("-" * 50)
    print(answer)