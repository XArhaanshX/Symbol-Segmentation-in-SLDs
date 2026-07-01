import os
import csv
import re

ROOT = r"c:\Users\arhaa\OneDrive\Symbol Segmentor"
OUT_DIR = os.path.join(ROOT, "reports", "restructure")
os.makedirs(OUT_DIR, exist_ok=True)

all_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    if any(ignore in dirpath for ignore in ['.git', '__pycache__', '.gemini', '.venv', 'venv']):
        continue
    for f in filenames:
        rel_path = os.path.relpath(os.path.join(dirpath, f), ROOT).replace('\\', '/')
        if rel_path.startswith("reports/restructure/"): continue
        all_files.append(rel_path)

mapping = []
deletion_candidates = []

def map_file(f):
    name = os.path.basename(f)
    ext = os.path.splitext(f)[1].lower()
    
    # 1. SRC files
    if f.startswith('src/'):
        if "stage" in name:
            if "58" in name or "5.8" in name: return f"exploration/structural_discriminator_research/scripts/{name}"
            if "59a" in name: return f"exploration/template_consistency_research/scripts/{name}"
            if "59b" in name: return f"exploration/symbol_existence_research/scripts/{name}"
            if "510" in name: return f"exploration/verification_cascade_research/scripts/{name}"
            return f"exploration/archived/scripts/{name}"
        
        # Production scripts logic (approximate)
        if "chamfer" in name: return f"src/template_matching/{name}"
        if "coverage" in name or "verification" in name or "ranking" in name: return f"src/verification/{name}"
        if "overlay" in name or "gallery" in name: return f"src/visualization/{name}"
        if "edge" in name or "candidate" in name: return f"src/candidate_generation/{name}"
        if "utils" in name: return f"src/common/{name}"
        
        # Default to pipeline if unclear but looks like core
        return f"src/pipeline/{name}"
    
    # 2. Data files
    if f.startswith('Data/'):
        if 'SLD' in name and ext == '.png': return f"data/raw/slds/{name}"
        if 'Symbol' in name or 'templates' in f.lower(): return f"data/templates/certified/{name}"
        return f"data/raw/{name}"
    
    # 3. Scratch scripts (Move to exploration/archived or flag for deletion)
    if f.startswith('scratch'):
        deletion_candidates.append(f)
        return f"exploration/archived/scratch/{name}"
        
    # 4. Outputs (Tabular vs Visual)
    if f.startswith('outputs/'):
        if ext in ['.png', '.jpg']: return f"outputs/visual/diagnostics/{name}"
        if ext in ['.csv', '.json']: return f"outputs/tabular/exports/{name}"
        return f"outputs/tabular/{name}"
    
    # 5. Reports
    if f.startswith('reports/'):
        if ext in ['.png', '.jpg']: 
            if "overlay" in name or "gallery" in name: return f"outputs/visual/overlays/{name}"
            return f"outputs/visual/diagnostics/{name}"
        
        if ext in ['.csv', '.json']:
            if "dataset" in name or "features" in name: return f"data/processed/candidate_features/{name}"
            return f"outputs/tabular/metrics/{name}"
            
        if ext == '.md':
            if "stage58" in name or "structural" in name: return f"reports/structural_discriminators/{name.replace('stage58_', '')}"
            if "stage59a" in name or "consistency" in name: return f"reports/structural_discriminators/{name.replace('stage59a_', '')}"
            if "stage59b" in name or "existence" in name: return f"reports/structural_discriminators/{name.replace('stage59b_', '')}"
            if "stage510" in name or "cascade" in name or "threshold" in name: return f"reports/verification_cascades/{name.replace('stage510_', '')}"
            if "visual_audit" in name: return f"reports/visual_audits/{name.replace('stage510_', '')}"
            if "ranking" in name: return f"reports/ranking_quality/{name}"
            
            if "stage" in name:
                return f"exploration/archived/reports/{name}"
            return f"reports/summaries/{name}"
            
    # 6. Docs
    if f.startswith('docs/'):
        return f
        
    if f == "README.md": return f
    
    # Unmatched
    return f"exploration/archived/misc/{name}"

for f in all_files:
    target = map_file(f)
    mapping.append({"current_path": f, "new_path": target})

# Write File Mapping Plan
with open(os.path.join(OUT_DIR, "file_mapping_plan.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["current_path", "new_path"])
    writer.writeheader()
    writer.writerows(mapping)

# Write Deletion Candidates
with open(os.path.join(OUT_DIR, "deletion_candidates.md"), "w", encoding="utf-8") as f:
    f.write("# Deletion Candidates\n\n")
    if not deletion_candidates:
        f.write("No files flagged for deletion.\n")
    for d in deletion_candidates:
        f.write(f"- {d}\n")

# Write Repository Audit
audit = f"""# Repository Audit

Total files inventoried: {len(all_files)}

### Top Level Destinations
- `src/`: {sum(1 for m in mapping if m['new_path'].startswith('src/'))}
- `data/`: {sum(1 for m in mapping if m['new_path'].startswith('data/'))}
- `outputs/`: {sum(1 for m in mapping if m['new_path'].startswith('outputs/'))}
- `reports/`: {sum(1 for m in mapping if m['new_path'].startswith('reports/'))}
- `exploration/`: {sum(1 for m in mapping if m['new_path'].startswith('exploration/'))}

### Identified Issues
- Found {len(deletion_candidates)} loose scratch files that are flagged for potential deletion.
- Multiple generated CSVs inside the `reports/` directory need migration to `data/processed/candidate_features/` or `outputs/tabular/`.
- Stage-based nomenclature in reports will be stripped during relocation.

"""
with open(os.path.join(OUT_DIR, "repository_audit.md"), "w", encoding="utf-8") as f:
    f.write(audit)

print("Restructure planning files generated successfully in reports/restructure/")
