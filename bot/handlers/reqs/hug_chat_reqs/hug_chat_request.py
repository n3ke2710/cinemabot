from hug_chat_config import chatbot


async def query_hugging_chat(prompt: str) -> str:
    """
    Sends a query to the Hugging Chat API using the hugchat library and returns the response.

    Args:
        prompt (str): The input string to send to the Hugging Chat API.

    Returns:
        str: The response from the Hugging Chat API.
    """
    response = chatbot.chat(prompt)

    # Преобразуем объект ответа в строку
    if hasattr(response, "content"):  # Если объект имеет атрибут content
        return response.content
    return str(response)  # В противном случае преобразуем в строку


async def search_movie_by_description(description: str) -> str:
    """
    Ищет фильм по описанию с помощью Hugging Chat API.
    """
    prompt = f"Найди фильм по следующему описанию: {description}"
    response = await query_hugging_chat(prompt)
    return response
