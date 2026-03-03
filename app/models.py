from dataclasses import dataclass, field
from typing import Any


@dataclass
class DingTalkApprovalPayload:
    event_type: str
    status: str
    instance_id: str
    applicant_name: str
    employee_no: str
    department: str
    is_outsourcing: bool = True
    requested_groups: list[str] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DingTalkApprovalPayload":
        required = [
            "event_type",
            "status",
            "instance_id",
            "applicant_name",
            "employee_no",
            "department",
        ]
        missing = [k for k in required if k not in data]
        if missing:
            raise ValueError(f"missing fields: {', '.join(missing)}")

        return cls(
            event_type=str(data["event_type"]),
            status=str(data["status"]),
            instance_id=str(data["instance_id"]),
            applicant_name=str(data["applicant_name"]),
            employee_no=str(data["employee_no"]),
            department=str(data["department"]),
            is_outsourcing=bool(data.get("is_outsourcing", True)),
            requested_groups=list(data.get("requested_groups", [])),
        )
