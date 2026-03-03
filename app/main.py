import hmac
import json
from http.server import BaseHTTPRequestHandler, HTTPServer

from app.models import DingTalkApprovalPayload
from app.services.account_builder import build_account_plan
from app.services.idempotency_store import IdempotencyStore
from app.services.provisioner import Provisioner
from app.settings import settings

store = IdempotencyStore(settings.idempotency_db)
provisioner = Provisioner()


def is_request_authorized(headers: dict[str, str], webhook_secret: str) -> bool:
    if not webhook_secret:
        return False

    received_secret = headers.get("X-Webhook-Secret", "")
    return hmac.compare_digest(received_secret, webhook_secret)


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/health":
            self._send(200, {"ok": True})
            return
        self._send(404, {"ok": False, "message": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/webhook/dingtalk/approval":
            self._send(404, {"ok": False, "message": "not found"})
            return

        if not is_request_authorized(dict(self.headers.items()), settings.webhook_secret):
            self._send(401, {"ok": False, "message": "unauthorized webhook request"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            data = json.loads(self.rfile.read(length).decode("utf-8"))
            payload = DingTalkApprovalPayload.from_dict(data)
        except Exception as exc:  # noqa: BLE001
            self._send(400, {"ok": False, "message": str(exc)})
            return

        if payload.event_type != "process_instance_change":
            self._send(400, {"ok": False, "message": "unsupported event_type"})
            return

        if payload.status != "COMPLETED":
            self._send(200, {"ok": True, "message": "ignored", "instance_id": payload.instance_id})
            return

        if store.seen(payload.instance_id):
            self._send(200, {"ok": True, "message": "idempotent_skip", "instance_id": payload.instance_id})
            return

        groups = list(payload.requested_groups)
        if payload.is_outsourcing:
            groups.append("GG-OUTSOURCING")

        plan = build_account_plan(
            display_name=payload.applicant_name,
            employee_no=payload.employee_no,
            ad_domain=settings.ad_domain,
            base_dn=settings.ad_base_dn,
            default_ou=settings.default_outsourcing_ou,
            groups=groups,
        )

        try:
            result = provisioner.provision(plan, payload.applicant_name, payload.employee_no)
        except Exception as exc:  # noqa: BLE001
            self._send(500, {"ok": False, "message": str(exc), "instance_id": payload.instance_id})
            return

        store.mark(payload.instance_id)
        self._send(
            200,
            {
                "ok": True,
                "message": "provisioned",
                "instance_id": payload.instance_id,
                "result": result,
            },
        )


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    server = HTTPServer((host, port), Handler)
    print(f"Server running on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    run()
