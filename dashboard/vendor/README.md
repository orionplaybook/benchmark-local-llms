# Third-party libraries (downloaded, not committed)

| File | Library | Version | Source | SHA-256 |
|---|---|---|---|---|
| `chart.umd.min.js` | Chart.js (MIT licence) | 4.4.1 | https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js | `81ffafe13c37e1b25793b020d446f4d9739b949dadb7f9f79d709a0cad781c2f` |

The files listed here are git-ignored. The first `./bench setup`, `./bench run`, `./bench dashboard` or
`./bench publish` downloads them and checks the SHA-256 (`src/benchlm/vendor.py`); a file that doesn't
match is never used. After that the dashboard works offline.

To upgrade Chart.js, change `CHARTJS_VERSION` and `CHARTJS_SHA256` in `src/benchlm/vendor.py` (hash of the
new file: `shasum -a 256 chart.umd.min.js`), update this table and THIRD_PARTY_NOTICES.md, then delete the
old file here so the next run downloads the new one.

Licence and copyright notice: see [THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).
