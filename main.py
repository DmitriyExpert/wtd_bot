import asyncio
import config
from aiogram import Bot, Dispatcher
from aiogram.types import Message


bot = Bot(token=config.TG_API_TOKEN)
dp = Dispatcher()


@dp.message()
async def cmd_start(message: Message):
    await message.answer("Привет!")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен")
