from app.database.requests import get_user_logged


async def is_user_logged_in(user_tg_id: int) -> int:
    return await get_user_logged(user_tg_id)