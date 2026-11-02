# Open Model Standings, October 2025

*Snapshot taken 2025-10-14. Only models with open weights are listed. Scores are updated weekly; see the methodology section below.*

**Columns:** **Arena Elo** is the crowd-sourced pairwise preference rating (style control on). **Agentic Index** is our composite of tool-use and multi-step task benchmarks (0–100). **Coding Index** is our composite of code-generation and repository-repair benchmarks (0–100).

| Rank | Model | Developer | Params | Arena Elo | 95% CI | Agentic Index | Coding Index | License |
|---|---|---|---|---|---|---|---|---|
| 1 | Meridian-70B-it | Meridian AI | 70B | 1342 | ±6 | 58.2 | 55.0 | Meridian Community |
| 2 | Corvus-32B-Chat | Corvus Collective | 32B | 1311 | ±5 | 51.9 | 50.3 | MIT |
| 3 | Halden-24B-Instruct | Halden Research | 24B | 1296 | ±7 | 45.1 | 46.8 | Apache 2.0 |
| 4 | Aurora-Lite 14B Instruct | Lumenfold Labs | 14.8B | 1287 | ±8 | 47.6 | 44.1 | Apache 2.0 |
| 5 | Meridian-15B-it | Meridian AI | 15B | 1279 | ±6 | 43.0 | 41.7 | Meridian Community |
| 6 | Corvus-13B-Chat | Corvus Collective | 13B | 1254 | ±7 | 38.4 | 37.2 | MIT |
| 7 | Aurora-Lite 8B Instruct | Lumenfold Labs | 8.2B | 1238 | ±9 | 39.0 | 35.6 | Apache 2.0 |
| 8 | Pellucid-9B | Pellucid | 9B | 1221 | ±10 | 31.5 | 33.9 | Pellucid Open |

### Movers this week

- **Aurora-Lite 14B Instruct** climbed two places after 4,100 new votes; its Arena Elo was 1269 in the September snapshot.
- **Halden-24B-Instruct** dropped one place despite a small gain in its Coding Index (46.1 → 46.8).
- **Pellucid-9B** entered the table for the first time.

### Methodology

Arena Elo uses a Bradley–Terry model fitted on all votes collected since the model's first appearance; models with fewer than 3,000 votes are not ranked. The Agentic Index averages normalised scores from BFCL v3, τ²-bench and two internal multi-step suites. The Coding Index averages LiveCodeBench, SWE-bench Verified and an internal repository-repair set. Index values are rounded to one decimal place and are not comparable with snapshots before August 2025, when the formula changed.
