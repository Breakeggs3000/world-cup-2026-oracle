# Safety policy

## Secrets and credentials

- Never commit `.env`, API keys, tokens, or credential files.
- Never print or log secrets in artifacts or session logs.
- Use environment variables or local-only config outside version control.

## Destructive operations

- No `rm -rf`, database drops, or force pushes without explicit user approval.
- No modifying production infrastructure unless the task explicitly requires it.
- Prefer dry-run or read-only commands when exploring unknown systems.

## Dependencies and supply chain

- Pin or document new dependencies in project config when adding to `src/`.
- Do not install packages from unverified sources.

## Data handling

- Do not exfiltrate private repo content to external services without approval.
- Redact PII from artifacts and memory files.

## When uncertain

Stop and ask. Failing closed is better than guessing on security-sensitive actions.
