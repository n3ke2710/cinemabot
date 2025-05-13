from hugchat import hugchat
import os
from dotenv import load_dotenv  # type: ignore


async def query_hugging_chat(prompt: str) -> str:
    """
    Sends a query to the Hugging Chat API using the hugchat library and returns the response.

    Args:
        prompt (str): The input string to send to the Hugging Chat API.

    Returns:
        str: The response from the Hugging Chat API.
    """
    preprompt = "Представь, что ты кинокритик. Посоветуй наиболее подходящий фильм под описание: \n"
    load_dotenv()  # Load environment variables from a .env file
    TOKEN = os.getenv("HUGGING_CHAT_TOKEN")  # Retrieve the token from environment variables

    if not TOKEN:
        raise ValueError("HUGGING_CHAT_TOKEN is not set in the environment variables.")

    chatbot = hugchat.ChatBot(token=TOKEN)  # Initialize ChatBot with the token
    response = chatbot.chat(preprompt + prompt)

    return response
