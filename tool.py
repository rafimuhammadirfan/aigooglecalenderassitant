# calendar_tools.py
import datetime
from dateutil import parser
import pytz
from langchain.tools import tool
from auth import create_service

# Scope: read & write
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Lazy init service (biar nggak langsung login saat import)
_service = None
def get_service():
    global _service
    if _service is None:
        _service = create_service("credential.json", "calendar", "v3", SCOPES)
    return _service

# --- Tools ---

@tool
def list_events_tool(max_results: int = 5) -> str:
    """Menampilkan sejumlah event terdekat dari Google Calendar pengguna."""
    service = get_service()
    now = datetime.datetime.utcnow().isoformat() + "Z"  # waktu sekarang (UTC)
    events_result = service.events().list(
        calendarId="primary", timeMin=now,
        maxResults=max_results, singleEvents=True, orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])
    if not events:
        return "Tidak ada event terdekat."

    text = "Event terdekat:\n"
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        text += f"- {start} | {event.get('summary', '(Tidak ada judul)')} (ID: {event['id']})\n"
    return text


@tool
def add_event_tool(summary: str, start_time: str, end_time: str, timezone: str = "Asia/Jakarta") -> str:
    """Menambahkan event baru ke Google Calendar.
    Format waktu harus bisa diparse (contoh: '2025-10-06 10:00').
    """
    service = get_service()

    try:
        start_dt = parser.parse(start_time)
        end_dt = parser.parse(end_time)

        # jika tanpa timezone, tambahkan default
        if start_dt.tzinfo is None:
            start_dt = pytz.timezone(timezone).localize(start_dt)
        if end_dt.tzinfo is None:
            end_dt = pytz.timezone(timezone).localize(end_dt)

        event = {
            "summary": summary,
            "start": {"dateTime": start_dt.isoformat(), "timeZone": timezone},
            "end": {"dateTime": end_dt.isoformat(), "timeZone": timezone},
        }

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        return f"✅ Event '{summary}' berhasil dibuat pada {start_dt}."
    except Exception as e:
        return f"❌ Gagal membuat event: {str(e)}"


@tool
def delete_event_tool(event_id: str) -> str:
    """Menghapus event berdasarkan ID (lihat ID saat list_events_tool)."""
    service = get_service()
    try:
        service.events().delete(calendarId="primary", eventId=event_id).execute()
        return f"🗑️ Event dengan ID {event_id} berhasil dihapus."
    except Exception as e:
        return f"❌ Gagal menghapus event: {str(e)}"


@tool
def recommend_time_tool(duration_minutes: int = 60, timezone: str = "Asia/Jakarta") -> str:
    """Merekomendasikan slot waktu kosong berdasarkan jadwal hari ini.
    Misalnya untuk cari waktu meeting 60 menit.
    """
    service = get_service()
    now = datetime.datetime.now(pytz.timezone(timezone))
    end_of_day = now.replace(hour=23, minute=59, second=59)

    # Ambil event hari ini
    events_result = service.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        timeMax=end_of_day.isoformat(),
        singleEvents=True,
        orderBy="startTime"
    ).execute()
    events = events_result.get("items", [])

    free_slots = []
    current_time = now

    for event in events:
        start = parser.parse(event["start"].get("dateTime", event["start"].get("date")))
        if start - current_time >= datetime.timedelta(minutes=duration_minutes):
            free_slots.append((current_time, start))
        end = parser.parse(event["end"].get("dateTime", event["end"].get("date")))
        current_time = max(current_time, end)

    if end_of_day - current_time >= datetime.timedelta(minutes=duration_minutes):
        free_slots.append((current_time, end_of_day))

    if not free_slots:
        return "❌ Tidak ada slot kosong tersedia hari ini."

    text = "Rekomendasi waktu kosong:\n"
    for slot in free_slots:
        text += f"- {slot[0].strftime('%H:%M')} s/d {slot[1].strftime('%H:%M')}\n"

    return text
