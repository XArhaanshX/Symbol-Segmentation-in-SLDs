# Repository Audit

Total files inventoried: 1451

### Top Level Destinations
- `src/`: 28
- `data/`: 25
- `outputs/`: 1198
- `reports/`: 122
- `exploration/`: 78

### Identified Issues
- Found 8 loose scratch files that are flagged for potential deletion.
- Multiple generated CSVs inside the `reports/` directory need migration to `data/processed/candidate_features/` or `outputs/tabular/`.
- Stage-based nomenclature in reports will be stripped during relocation.

