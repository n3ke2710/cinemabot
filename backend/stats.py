import time
import asyncio
import aiofiles # type: ignore

from config import bot

async def add_to_history(id, movie) -> None:
    if not isinstance(id, int):
        raise TypeError("Id is not integer")
    if not isinstance(movie, str):
        raise TypeError("Movie is not string")
    async with aiofiles.open(f"./backend/temp/{id}/history.log", mode="a") as file:
        await file.write(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}: {movie}\n")


async def get_history(id, count=10) -> str:
    if not isinstance(id, int):
        raise TypeError("Id is not integer")
    if not isinstance(count, int):
        raise TypeError("Count is not integer")
    if count <= 0:
        raise ValueError("Count must be greater than 0")
    
    try:
        async with aiofiles.open(f"./backend/temp/{id}/history.log", mode="r") as file:
            lines = await file.readlines()
            recent_logs = lines[-count:]
            message = "".join(recent_logs)
    except FileNotFoundError:
        message = "No history found."
    
    return message