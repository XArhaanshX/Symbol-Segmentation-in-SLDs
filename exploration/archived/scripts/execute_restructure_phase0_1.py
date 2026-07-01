import os
import csv
import ast

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
        if rel_path == "execute_restructure_phase0_1.py": continue
        all_files.append(rel_path)

mapping = []
scratch_candidates = []

def map_file(f):
    name = os.path.basename(f)
    ext = os.path.splitext(f)[1].lower()
    
    if f.startswith('src/'):
        if "stage" in name:
            if "58" in name or "5.8" in name: return f"exploration/structural_discriminator_research/scripts/{name}"
            if "59a" in name: return f"exploration/template_consistency_research/scripts/{name}"
            if "59b" in name: return f"exploration/symbol_existence_research/scripts/{name}"
            if "510" in name: return f"exploration/verification_cascade_research/scripts/{name}"
            return f"exploration/archived/scripts/{name}"
        
        if "chamfer" in name or "template" in name: return f"src/template_matching/{name}"
        if "coverage" in name or "verification" in name or "ranking" in name or "score" in name: return f"src/verification/{name}"
        if "overlay" in name or "gallery" in name or "visual" in name: return f"src/visualization/{name}"
        if "edge" in name or "candidate" in name or "localization" in name: return f"src/candidate_generation/{name}"
        if "utils" in name: return f"src/common/{name}"
        if "orchestrator" in name or "pipeline" in name: return f"src/pipeline/{name}"
        
        return f"src/pipeline/{name}"
    
    if f.startswith('Data/'):
        if 'SLD' in name and ext == '.png': return f"data/raw/slds/{name}"
        if 'Symbol' in name or 'templates' in f.lower(): return f"data/templates/certified/{name}"
        return f"data/raw/{name}"
        
    if f.startswith('scratch'):
        scratch_candidates.append(f)
        return f"exploration/archived/scratch/{name}"
        
    if f.startswith('outputs/'):
        if ext in ['.png', '.jpg']: return f"outputs/visual/diagnostics/{name}"
        if ext in ['.csv', '.json']: return f"outputs/tabular/exports/{name}"
        return f"outputs/tabular/{name}"
        
    if f.startswith('reports/'):
        if ext in ['.png', '.jpg']: 
            if "overlay" in name or "gallery" in name: return f"outputs/visual/overlays/{name}"
            return f"outputs/visual/diagnostics/{name}"
        
        if ext in ['.csv', '.json']:
            if "dataset" in name or "features" in name: return f"data/processed/candidate_features/{name}"
            return f"outputs/tabular/metrics/{name}"
            
        if ext == '.md':
            if "stage58" in name or "structural" in name: return f"reports/structural_discriminators/{name}"
            if "stage59a" in name or "consistency" in name: return f"reports/structural_discriminators/{name}"
            if "stage59b" in name or "existence" in name: return f"reports/structural_discriminators/{name}"
            if "stage510" in name or "cascade" in name or "threshold" in name: return f"reports/verification_cascades/{name}"
            if "visual_audit" in name: return f"reports/visual_audits/{name}"
            if "ranking" in name: return f"reports/ranking_quality/{name}"
            
            if "stage" in name:
                return f"exploration/archived/reports/{name}"
            return f"reports/summaries/{name}"
            
    if f.startswith('docs/'): return f
    if f == "README.md": return f
    
    return f"exploration/archived/misc/{name}"

# PHASE 0
for f in all_files:
    target = map_file(f)
    assert os.path.basename(f) == os.path.basename(target), f"FILENAME CHANGED! {f} -> {target}"
    mapping.append({"current_path": f, "new_path": target})

with open(os.path.join(OUT_DIR, "file_mapping_plan.csv"), "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["current_path", "new_path"])
    writer.writeheader()
    writer.writerows(mapping)

print(f"Phase 0 completed. {len(mapping)} files mapped.")

# Count pre-migration stats for Phase 7
orig_py = sum(1 for f in all_files if f.endswith('.py'))
orig_md = sum(1 for f in all_files if f.endswith('.md'))
orig_data = sum(1 for f in all_files if f.startswith('Data/'))
orig_out = sum(1 for f in all_files if f.startswith('outputs/'))

with open(os.path.join(OUT_DIR, "pre_migration_counts.txt"), "w") as f:
    f.write(f"orig_total={len(all_files)}\n")
    f.write(f"orig_py={orig_py}\n")
    f.write(f"orig_md={orig_md}\n")
    f.write(f"orig_data={orig_data}\n")
    f.write(f"orig_out={orig_out}\n")

# PHASE 1: Import Dependency Audit
print("Running Phase 1: Import Dependency Audit...")
audit_md = "# Import Dependency Audit\n\n"
audit_md += "| Original Path | Proposed Path | Imported Modules | Imported By | Dep Count | Risk Level |\n"
audit_md += "|---|---|---|---|---|---|\n"

# 1. Gather all python files
py_files = [m for m in mapping if m['current_path'].endswith('.py')]
module_graph = {m['current_path']: [] for m in py_files}
imported_by = {m['current_path']: [] for m in py_files}

# Build module name to path mapping for our internal files
# Usually people do `from src.localization.stage58... import ...`
# Let's map src path logic
path_to_mod = {}
for p in py_files:
    mod = p['current_path'].replace('/', '.').replace('\\', '.').replace('.py', '')
    path_to_mod[mod] = p['current_path']

for p in py_files:
    try:
        with open(os.path.join(ROOT, p['current_path']), 'r', encoding='utf-8') as f:
            code = f.read()
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_graph[p['current_path']].append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    module_graph[p['current_path']].append(node.module)
    except Exception as e:
        module_graph[p['current_path']].append(f"ERROR: {e}")

# Resolve to internal imports
for p in py_files:
    for imp in module_graph[p['current_path']]:
        if imp in path_to_mod:
            imported_by[path_to_mod[imp]].append(p['current_path'])
        else:
            # Maybe partial matching
            for mod, pth in path_to_mod.items():
                if imp.startswith(mod):
                    imported_by[pth].append(p['current_path'])

for p in py_files:
    orig = p['current_path']
    new_p = p['new_path']
    deps = module_graph[orig]
    ib = imported_by[orig]
    
    # Assess Risk
    risk = "LOW RISK"
    if len(ib) > 5 or "utils" in orig or "config" in orig: risk = "HIGH RISK"
    elif len(ib) > 2: risk = "MEDIUM RISK"
    
    imp_str = ", ".join(deps[:5]) + ("..." if len(deps)>5 else "")
    ib_str = ", ".join(ib[:3]) + ("..." if len(ib)>3 else "")
    
    if not imp_str: imp_str = "None"
    if not ib_str: ib_str = "None"
    
    audit_md += f"| {orig} | {new_p} | {imp_str} | {ib_str} | {len(deps)} | **{risk}** |\n"

with open(os.path.join(OUT_DIR, "import_dependency_audit.md"), "w", encoding="utf-8") as f:
    f.write(audit_md)

print("Phase 1 completed.")
