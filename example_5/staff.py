import httpx

from example_5 import config

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


async def get_employees_calendars(emails, start, end):
    await update_staff_token()
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://staff.skbkontur.ru/api/calendars",
            params={"email": emails, "start": start.isoformat(), "end": end.isoformat()},
            headers={"Authorization": "Bearer " + STAFF_TOKEN},
        )
    if response.status_code == 200:
        return response.json()["calendar"]

    response.raise_for_status()


async def create_calendar_event(emails: list[str], start, end):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://staff.skbkontur.ru/api/calendar",
            json={
                "start": start.isoformat(),
                "end": end.isoformat(),
                "key": None,
                "location": "",
                "subject": f"Автоматическая встреча от {config.USER_EMAIL}",
                "description": "",
                "hasVideoConference": True,
                "requiredAttendees": [{"mailbox": email} for email in emails]
            },
            headers={"Authorization": "Bearer " + STAFF_TOKEN},
        )
    if response.status_code == 200:
        return

    response.raise_for_status()
