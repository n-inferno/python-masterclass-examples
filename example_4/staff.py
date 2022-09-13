import httpx

from example_4 import config

STAFF_TOKEN = "token"


async def update_staff_token():
    global STAFF_TOKEN

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://passport.skbkontur.ru/connect/token",
            data={
                "grant_type": "password",
                "scope": "profiles",
                "username": config.LOGIN,
                "password": config.PASSWORD,
            },
            auth=httpx.BasicAuth(config.CLIENT_ID, config.CLIENT_SECRET),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
    if response.status_code == 200:
        STAFF_TOKEN = response.json()["access_token"]
        return

    response.raise_for_status()


async def search_person_email(query: str) -> list[dict[str, str]]:
    await update_staff_token()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://staff.skbkontur.ru/api/Suggest/bytype",
            params={"Q": query, "Types": 7},
            headers={"Authorization": "Bearer " + STAFF_TOKEN},
        )
    if response.status_code == 200:
        data = response.json()["items"]
        return [{"name": item["name"], "email": item["email"]} for item in data]
    response.raise_for_status()


