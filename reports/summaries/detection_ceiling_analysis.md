# Detection Ceiling Analysis

| Classification | Count | Percentage |
| :--- | :---: | :---: |
| LOCALIZED_AND_HIGHLY_RANKED (Rank <= 1000) | 297 | 55.5% |
| LOCALIZED_BUT_POORLY_RANKED (Rank > 1000) | 223 | 41.7% |
| NOT_LOCALIZED (Not in Candidate Pool) | 15 | 2.8% |

## Required Questions
1. **How many symbols are successfully localized but ranked poorly?** 223
2. **How many symbols are never localized at all?** 15
3. **Is ranking or localization the dominant failure mode?** 
   Ranking is a failure mode for 223 symbols, but absolute localization failure accounts for 15 symbols. Both contribute significantly.
4. **Does the dominant failure mode change by scale regime?** (To be answered in the root cause verdict after regime analysis).
