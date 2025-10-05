AI Chatbot berbasis **LangChain + Google Gemini** yang terintegrasi dengan **Google Calendar**.  
Chatbot ini bisa:
- Melihat jadwal terdekat
- Menambahkan event baru ke Google Calendar
- Menghapus event tertentu
- Merekomendasikan waktu kosong untuk meeting/jadwal

Dibuat menggunakan **Streamlit** untuk UI, sehingga mudah digunakan via web.

---

## 📌 Fitur
- 🔑 Login via **Google OAuth**
- 📅 Akses Google Calendar pengguna
- 💬 Chatbot dengan LLM Gemini
- 🛠 Tools Calendar:
  - `list_events` → melihat 5 event terdekat
  - `add_event` → menambahkan event
  - `delete_event` → menghapus event
  - `recommend_time` → memberikan rekomendasi waktu kosong


🔑 Setup Google Calendar API
1. Buka Google Cloud Console.
2. Buat Project baru atau gunakan project yang sudah ada.
3. Aktifkan API: Google Calendar API
4. Buat OAuth client ID: Application type: Desktop app, Download file credentials.json.
6. Taruh file credentials.json di root project 
