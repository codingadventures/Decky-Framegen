# Test fixtures

## `Compatibility-List.md`

Snapshot of the live OptiScaler wiki compatibility list:

https://github.com/optiscaler/OptiScaler/wiki/Compatibility-List

Refresh locally when the wiki changes materially:

```bash
curl -fsSL -o tests/fixtures/Compatibility-List.md \
  "https://raw.githubusercontent.com/wiki/optiscaler/OptiScaler/Compatibility-List.md"
python3 -m unittest discover -s tests -v
```

Tests assert parser output against this file so regressions in markdown parsing or name normalization are caught offline without hitting the network on CI/device.
