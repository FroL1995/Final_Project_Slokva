from typing import Any, Optional, Dict, List
from aiohttp import ClientSession, ClientTimeout, ClientError

from config import API_BASE_URL, STEAM_API_KEY


async def request_api(
    url: str,
    params: Optional[Dict[str, Any]] = None,
    headers: Optional[Dict[str, Any]] = None
) -> Optional[Dict[str, Any]]:
    """Асинхронный запрос к API."""
    if params is None:
        params = {}

    if headers is None:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "x-rapidapi-key": STEAM_API_KEY,
            "x-rapidapi-host": "steam2.p.rapidapi.com",
        }

    timeout = ClientTimeout(total=10)
    try:
        async with ClientSession(timeout=timeout) as session:
            async with session.get(url, params=params, headers=headers) as response:
                if response.status != 200:
                    print(f"Ошибка: Получен статус {response.status} при запросе {url}")
                    return None
                return await response.json()

    except ClientError as e:
        print(f"Сетевая ошибка: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

    return None


async def search_games(term: str, page: int) -> List[Dict[str, Any]]:
    """Поиск игр по ключевому слову."""
    url = f"{API_BASE_URL}/search/{term}/page/{page}"
    result = await request_api(url)
    print(result)

    games = []
    if not result:
        return games

    for item in result:
        games.append({
            "app_id": item.get("appId"),
            "title": item.get("title"),
            "steam_url": item.get("url", "-"),
            "img_url": item.get("img_url"),
            "released": item.get("released"),
            "price": item.get("price") or "Нет информации",
        })
    return games


async def app_detail(app_id: int) -> Optional[Dict[str, Any]]:
    """Получение детальной информации об игре."""
    url = f"{API_BASE_URL}/app/{app_id}"
    result = await request_api(url)
    if not result:
        return None

    return {
        "app_id": result.get("appId"),
        "title": result.get("title"),
        "description": result.get("description", "Описание недоступно"),
        "price": result.get("price", "Нет информации"),
        "release_date": result.get("release_date", "Неизвестно"),
        "developer": result.get("developer", "Неизвестно"),
        "publisher": result.get("publisher", "Неизвестно"),
        "genres": result.get("genres", []),
    }
