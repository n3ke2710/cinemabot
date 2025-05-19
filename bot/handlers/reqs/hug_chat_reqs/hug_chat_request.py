from bot.handlers.reqs.hug_chat_reqs.hug_chat_config import chatbot


async def query_hugging_chat(prompt: str) -> str:
    """
    Sends a query to the Hugging Chat API using the hugchat library and returns the response.

    Args:
        prompt (str): The input string to send to the Hugging Chat API.

    Returns:
        str: The response from the Hugging Chat API.
    """
    preprompt = "Представь, что ты кинокритик. Посоветуй наиболее подходящий фильм под описание. Формат ответа: номер. название(год). Описание:\n"

    response = chatbot.chat(preprompt + prompt)

    # Преобразуем объект ответа в строку
    if hasattr(response, "content"):  # Если объект имеет атрибут content
        return response.content
    return str(response)  # В противном случае преобразуем в строку
