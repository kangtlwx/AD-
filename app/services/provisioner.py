import json
import subprocess
from dataclasses import asdict

from app.services.account_builder import AccountPlan
from app.settings import settings


class Provisioner:
    def provision(self, plan: AccountPlan, display_name: str, employee_no: str) -> dict:
        if settings.dry_run:
            return {"dry_run": True, **asdict(plan)}

        payload = {
            "display_name": display_name,
            "employee_no": employee_no,
            **asdict(plan),
        }

        cmd = [
            settings.powershell_path,
            "-File",
            settings.provision_script,
            "-InputJson",
            json.dumps(payload, ensure_ascii=False),
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode != 0:
            raise RuntimeError(f"Provision failed: {result.stderr.strip()}")

        out = result.stdout.strip()
        return json.loads(out) if out else {"ok": True}
