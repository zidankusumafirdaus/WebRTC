import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from apps.schemas.report_schemas import ReportCreateSchema


def main() -> None:
    schema = ReportCreateSchema()
    payload = {
        "conversation_id": 123,
        "title": "Hasil Konseling",
        "content": "Ringkasan sesi dan rekomendasi.",
    }
    result = schema.load(payload)
    print("OK", result)


if __name__ == "__main__":
    main()
