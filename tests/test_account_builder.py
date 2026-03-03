from app.services.account_builder import build_account_plan


def test_build_account_plan_basic() -> None:
    plan = build_account_plan(
        display_name="Zhang San",
        employee_no="A10086",
        ad_domain="longsys.com",
        base_dn="DC=longsys,DC=com",
        default_ou="OU=Outsourcing,DC=longsys,DC=com",
        groups=["GG-RD-BASIC", "GG-OUTSOURCING"],
    )

    assert plan.sam_account_name == "zhangsan"
    assert plan.upn == "zhangsan@longsys.com"
    assert "GG-ALL-STAFF" in plan.groups


def test_build_account_plan_fallback_to_employee_no() -> None:
    plan = build_account_plan(
        display_name="张三",
        employee_no="A10086",
        ad_domain="longsys.com",
        base_dn="DC=longsys,DC=com",
        default_ou="OU=Outsourcing,DC=longsys,DC=com",
        groups=[],
    )

    assert plan.sam_account_name == "ua10086"
