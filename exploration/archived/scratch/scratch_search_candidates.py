with open("PRD/PRD_Symbol_Localization.md", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()

# Search for "raw_candidates"
for i, line in enumerate(lines):
    if "raw_candidates" in line.lower() or "ranked_candidates" in line.lower():
        print(f"--- Line {i+1} ---")
        for j in range(max(0, i-5), min(len(lines), i+6)):
            safe_text = lines[j].encode("ascii", "ignore").decode("ascii")
            print(f"{j+1}: {safe_text}")
