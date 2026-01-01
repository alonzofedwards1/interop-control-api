import json
from pathlib import Path

BASE_DIR = Path("data/pd")
BASE_DIR.mkdir(parents=True, exist_ok=True)


class PDStorage:
    def save_pd_response(
        self,
        correlation_id: str,
        payload: str,
        payload_type: str,
        message_type: str,
    ) -> None:
        path = BASE_DIR / f"{correlation_id}_response.json"
        path.write_text(
            json.dumps(
                {
                    "payload_type": payload_type,
                    "message_type": message_type,
                    "payload": payload,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    def update_execution(self, correlation_id: str, update: dict) -> None:
        path = BASE_DIR / f"{correlation_id}_execution.json"
        if not path.exists():
            return

        data = json.loads(path.read_text(encoding="utf-8"))
        data.update(update)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def create_execution(
        self,
        correlation_id: str,
        patient_reference: str,
        status: str,
        triggered_at: str,
    ) -> None:
        path = BASE_DIR / f"{correlation_id}_execution.json"
        path.write_text(
            json.dumps(
                {
                    "correlation_id": correlation_id,
                    "patient_reference": patient_reference,
                    "status": status,
                    "triggered_at": triggered_at,
                },
                indent=2,
            ),
            encoding="utf-8",
        )
