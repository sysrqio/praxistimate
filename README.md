# praxistimate

Open-source CLI to audit **German dental practice TI readiness** (ePA 3.0, KIM 1.5,
§390 SGB V IT security checklist) from a local **practice manifest** — no patient data,
no cloud required.

## Quick start

```bash
pip install .
praxistimate audit --manifest examples/praxis-manifest.json
```

Exit codes: `0` OK · `2` policy violation · `1` error

## Manifest

See `examples/praxis-manifest.json`. Fields are self-declared metadata from the
practice or IT service provider (PVS version, KIM version, connector generation, etc.).

## Rules

Bundled ruleset `kzbv-ti-2026.1` in `praxistimate/rules/default.yaml`. Override with
`--rules path/to/custom.yaml`.

## License

MIT — see [LICENSE](LICENSE).

## Related

Incubator evaluation docs live in the private **sysrq-io/Incubator** project `PraxisTiMate`;
this repo contains **no** internal scores or founder data.
