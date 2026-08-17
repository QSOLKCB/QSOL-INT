# Compatibility reports

QSOL-INT compatibility reports are deterministic, derived integration artifacts.

They are not parent protocol truth.

PR #3 reports are scoped to exact pinned parent evidence and must carry `live_parent_freshness: "untested"` until PR #2 drift tooling provides current-parent evidence.

Canonical generated baseline:

- `reports/pinned-bootstrap.json`

Regenerate and verify with:

```bash
python3 tools/run_batteries.py --write-report compatibility/reports/pinned-bootstrap.json
python3 tools/run_batteries.py --validate-report compatibility/reports/pinned-bootstrap.json
```
