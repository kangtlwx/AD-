# DingTalk 审批自动开通 AD/Exchange（longsys.com）示例

本项目提供一个可直接演示的最小可用实现（纯 Python 标准库）：

- 接收钉钉审批完成回调（Webhook）
- 解析入职字段并做校验
- 生成 `samAccountName`、UPN、邮箱地址（域名固定为 `longsys.com`）
- 幂等处理（同一流程实例重复推送不会重复建号）
- 调用 PowerShell 脚本执行 AD + Exchange 开通（支持 Dry Run 演示模式）

> 默认 `DRY_RUN=true`，仅演示流程，不会真的连接 AD/Exchange。

## 目录结构

```text
app/
  main.py                 # HTTP 服务入口
  models.py               # 回调数据模型
  settings.py             # 环境配置
  services/
    account_builder.py    # 账号生成规则
    idempotency_store.py  # 幂等存储（SQLite）
    provisioner.py        # AD/Exchange 执行器
scripts/
  Create-AdExchangeUser.ps1   # PowerShell 开通脚本
demos/
  sample_approval.json    # 演示回调样例
tests/
  test_account_builder.py
```

## 运行方式

### 1) 启动服务

```bash
python -m app.main
```

### 2) 发送演示请求

```bash
curl -X POST 'http://127.0.0.1:8000/webhook/dingtalk/approval' \
  -H 'Content-Type: application/json' \
  -H 'X-Webhook-Secret: demo-secret' \
  --data @demos/sample_approval.json
```

## 环境变量

- `AD_DOMAIN=longsys.com`
- `AD_BASE_DN=DC=longsys,DC=com`
- `DEFAULT_OUTSOURCING_OU=OU=Outsourcing,DC=longsys,DC=com`
- `DRY_RUN=true`（默认）
- `POWERSHELL_PATH=pwsh`
- `PROVISION_SCRIPT=./scripts/Create-AdExchangeUser.ps1`
- `IDEMPOTENCY_DB=./data/idempotency.db`
- `WEBHOOK_SECRET`（必填，必须与请求头 `X-Webhook-Secret` 一致）

## 对接真实 AD/Exchange

1. 将 `DRY_RUN=false`
2. 确保运行机器可连接域控与 Exchange
3. 在 `scripts/Create-AdExchangeUser.ps1` 中替换为真实命令：
   - `New-ADUser`
   - `Enable-Mailbox` / `New-RemoteMailbox`
   - 组策略、初始密码、强制改密、离职回收策略
