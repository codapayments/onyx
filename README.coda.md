# Coda fork notes (`codapayments/onyx`)

## Model (hybrid — not HyperDX trunk)

- **What we run** is always a public upstream release pin: branch `release/vX.Y.Z` cut from tag `vX.Y.Z`.
- **Coda patches** stack as commits on that release line. Image tags: `vX.Y.Z-coda.N`.
- **Upgrade**: cut `release/vX.Y.Z+1` from the new upstream tag → cherry-pick Coda commits → drop patches upstream absorbed → build `vX.Y.Z+1-coda.1` → flip Helm in `coda-sip-sail-onyx`.
- Fork **`main`** mirrors upstream for convenience only — **do not** build or pin Helm from it.

See DX-2557 / DX-2539.

## Packaging (Dagger)

First-party ECR images (`sip/sail/onyx-{backend,web-server,model-server}`) via Dagger **0.21.9** (same pin as SAIL GitOps / Engineering Metrics):

```sh
mise setup          # dagger develop (Docker required)
mise lint           # dockerfile presence (cheap PR gate)
mise package        # backend (runtime) + web + model-server
```

| mise / dagger | Image |
| --- | --- |
| `backend` | `backend/Dockerfile` target `runtime` |
| `web` | `web/Dockerfile` |
| `model-server` | `backend/Dockerfile.model_server` |

Optional: `--base-image-registry` for the Coda ECR Docker Hub pull-through cache on TeamCity agents.
