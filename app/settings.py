import os
from dataclasses import dataclass


@dataclass
class Settings:
    ad_domain: str = os.getenv("AD_DOMAIN", "longsys.com")
    ad_base_dn: str = os.getenv("AD_BASE_DN", "DC=longsys,DC=com")
    default_outsourcing_ou: str = os.getenv(
        "DEFAULT_OUTSOURCING_OU", "OU=Outsourcing,DC=longsys,DC=com"
    )
    dry_run: bool = os.getenv("DRY_RUN", "true").lower() == "true"
    powershell_path: str = os.getenv("POWERSHELL_PATH", "pwsh")
    provision_script: str = os.getenv(
        "PROVISION_SCRIPT", "./scripts/Create-AdExchangeUser.ps1"
    )
    idempotency_db: str = os.getenv("IDEMPOTENCY_DB", "./data/idempotency.db")


settings = Settings()
