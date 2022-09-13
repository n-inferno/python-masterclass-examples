# Про алгоритм можно почитать тут:
# https://stackoverflow.com/questions/34425237/algorithm-to-find-meeting-time-slots-where-all-participants-are-available
from datetime import timedelta, datetime
from zoneinfo import ZoneInfo

import config


async def get_meetings_options(options, meeting_duration, from_dt, to_dt):
    existing_meetings = [[from_dt.replace(second=0, microsecond=0, minute=0, hour=0), from_dt], [to_dt, to_dt]]

    # удаляем нерабочее время
    day_start = from_dt

    while day_start <= to_dt:
        day_beginning = day_start.replace(second=0, microsecond=0, minute=0, hour=0)
        if day_start.weekday() < 5:
            existing_meetings.append([day_beginning, day_beginning.replace(day=(day_start + timedelta(days=1)).day)])
        else:
            existing_meetings.append([day_beginning, day_beginning.replace(hour=10)])
            existing_meetings.append(
                [day_beginning.replace(hour=18), day_beginning.replace(day=(day_start + timedelta(days=1)).day)]
            )

        day_start += timedelta(days=1)

    # вытаскиваем интервалы из данных
    for email, meetings in options.items():
        for meeting in meetings:
            if meeting["busyType"] == "busy":
                date_from = datetime.strptime(meeting["start"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=ZoneInfo("UTC"))
                date_to = datetime.strptime(meeting["end"], "%Y-%m-%dT%H:%M:%S.%fZ").replace(tzinfo=ZoneInfo("UTC"))

                existing_meetings.append([date_from, date_to])

    # ищем пересечения
    existing_meetings.sort(key=lambda x: x[0], reverse=True)
    tmp = []

    while existing_meetings:
        pair = existing_meetings.pop()

        if tmp and tmp[-1][1] >= pair[0]:
            tmp[-1][1] = max(pair[1], tmp[-1][1])
        else:
            tmp.append(pair)

    free_intervals = []
    for i in range(len(tmp) - 1):
        free_intervals.append([tmp[i][1], tmp[i + 1][0]])

    # отбираем варианты исходя из длительности встречи
    suggestions = []
    meeting_duration = timedelta(minutes=meeting_duration)
    for start, end in free_intervals:
        start = start.astimezone(ZoneInfo(config.USER_TIME_ZONE))
        end = end.astimezone(ZoneInfo(config.USER_TIME_ZONE))

        while start + meeting_duration <= end:
            suggestions.append([start, start + meeting_duration])
            start += meeting_duration

    return suggestions
