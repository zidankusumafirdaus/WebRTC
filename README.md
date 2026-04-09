# Chat Service

Minimal setup and CI-ready test target for the Flask chat backend.

## Quickstart

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the server

```powershell
python server.py
```

## Run tests

```powershell
pip install -r requirements-dev.txt
pytest -q
```

## Call & Video Call API (HTTP)

All endpoints require JWT and role (`user` or `counselor`).

User routes are under `/api/user`, counselor routes under `/api/counselor`.

- `POST /calls/start` → body: `{ "conversation_id": 123, "call_type": "audio|video" }`
- `POST /calls/<call_session_id>/answer`
- `POST /calls/<call_session_id>/end` → body: `{ "ended_reason": "hangup|busy|failed" }`
- `GET /calls` → list recent calls
- `GET /calls/<call_session_id>` → get a call session

## WebRTC Signaling (Socket.IO)

Socket events (server uses JWT from `Authorization: Bearer <token>` or `?token=`):

- `join`: `{ "room_id": "<call_session_id>" }`
- `offer`: `{ "room_id": "<call_session_id>", "sdp": { ... } }`
- `answer`: `{ "room_id": "<call_session_id>", "sdp": { ... } }`
- `candidate`: `{ "room_id": "<call_session_id>", "candidate": { ... } }`
