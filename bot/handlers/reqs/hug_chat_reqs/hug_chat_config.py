import os
from dotenv import load_dotenv  # type: ignore
from hugchat import hugchat # type: ignore
from hugchat.login import Login # type: ignore

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWD = os.getenv("PASSWD")

if not EMAIL:
    raise ValueError("EMAIL не найден в переменных окружения")

if not PASSWD:
    raise ValueError("PASSWD не найден в переменных окружения")

cookie_path_dir = "./ai/cookies/" # NOTE: trailing slash (/) is required to avoid errors
sign = Login(EMAIL, PASSWD)
cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

chatbot = hugchat.ChatBot(cookies=cookies.get_dict())