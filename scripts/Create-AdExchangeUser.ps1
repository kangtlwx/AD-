param(
    [Parameter(Mandatory = $true)]
    [string]$InputJson
)

# 演示脚本：生产环境中请改为真实 AD / Exchange 命令
# 示例：
# Import-Module ActiveDirectory
# $data = $InputJson | ConvertFrom-Json
# New-ADUser -Name $data.display_name -SamAccountName $data.sam_account_name ...
# Enable-Mailbox -Identity $data.sam_account_name -Alias $data.sam_account_name

$data = $InputJson | ConvertFrom-Json

$result = [ordered]@{
    ok = $true
    dry_run = $false
    sam_account_name = $data.sam_account_name
    upn = $data.upn
    email = $data.email
    ou_path = $data.ou_path
    groups = $data.groups
    message = "PowerShell script executed"
}

$result | ConvertTo-Json -Depth 6
