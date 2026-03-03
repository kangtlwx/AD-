import re
import unicodedata
from dataclasses import dataclass
from typing import List


@dataclass
class AccountPlan:
    sam_account_name: str
    upn: str
    email: str
    ou_path: str
    groups: List[str]


def _normalize_ascii(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_text = re.sub(r"[^a-zA-Z0-9]", "", ascii_text).lower()
    return ascii_text


def build_account_plan(
    display_name: str,
    employee_no: str,
    ad_domain: str,
    base_dn: str,
    default_ou: str,
    groups: List[str],
) -> AccountPlan:
    # 中文名等无法转 ASCII 时，回退工号
    sam = _normalize_ascii(display_name)
    if not sam:
        sam = f"u{employee_no}".lower()

    # AD 常见建议长度限制（示例）
    sam = sam[:20]
    upn = f"{sam}@{ad_domain}"
    email = upn
    final_groups = ["GG-ALL-STAFF", *groups]

    return AccountPlan(
        sam_account_name=sam,
        upn=upn,
        email=email,
        ou_path=default_ou or f"OU=Users,{base_dn}",
        groups=list(dict.fromkeys(final_groups)),
    )
