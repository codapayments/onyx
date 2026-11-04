# Coda fork notes (`codapayments/onyx`)

## Model (hybrid — not HyperDX trunk)

- **What we run** is always a public upstream release pin: branch `release/vX.Y.Z` cut from tag `vX.Y.Z`.
- **Coda patches** stack as commits on that release line. Image tags: `vX.Y.Z-coda.N`.
- **Upgrade**: cut `release/vX.Y.Z+1` from the new upstream tag → cherry-pick Coda commits → drop patches upstream absorbed → build `vX.Y.Z+1-coda.1` → flip Helm in `coda-sip-sail-onyx`.
- Fork **`main`** mirrors upstream for convenience only — **do not** build or pin Helm from it.

See DX-2557 / DX-2539.

## Current pin

| Item | Value |
| --- | --- |
| Upstream tag | `v5.0.2` |
| Commit | `20f4c5fe63995f60825dc43e481ef290dd88f6fc` |
| Branch | `release/v5.0.2` |

## Coda patches on `release/v5.0.2`

1. Forward `user` / `chat_session_id` via `extra_body` for OpenAI-compatible providers (upstream PR [#10499](https://github.com/onyx-dot-app/onyx/pull/10499) / issue [#10461](https://github.com/onyx-dot-app/onyx/issues/10461)) so LiteLLM End User works with our gateway.
