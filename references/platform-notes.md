# Platform Notes

Use this file only when the task includes app installation, deployment wiring, or notifications to external collaboration tools.

## Lark / Feishu

Before installation or rollout:

- Confirm the target tenant and app identity
- Confirm whether tenant admin approval is required
- Confirm the bot or app scopes match the requested behavior
- Confirm callback URLs, event subscriptions, and secret handling are prepared
- Ask the user to approve the exact installation path in OpenClaw before dispatching any install or deploy action

Do not assume a Lark app can be installed just because code is ready.

## Telegram

Before notifications:

- Confirm the bot account and target chat or group
- Confirm the user wants final notifications in DM or group
- Avoid changing bot routing unless the user asked for it

## Generic Platform Rule

For any platform:

- Keep user-facing approval in OpenClaw
- Keep credentials and secret confirmation in OpenClaw
- Dispatch implementation and automation only after the target platform details are confirmed
- If platform permissions are unclear, stop and ask for the exact missing permission or approval path
