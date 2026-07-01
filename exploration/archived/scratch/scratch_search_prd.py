with open("PRD/PRD_Symbol_Localization.md", "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()

# Search for Section 5/6 or Stage 3 headings
stage3_headings = []
for i, line in enumerate(lines):
    if "stage 3" in line.lower() or "candidate generation" in line.lower() or "raw_candidates" in line.lower():
        stage3_headings.append((i+1, line))

print(f"Total matching lines: {len(stage3_headings)}")
for idx, text in stage3_headings[:100]:
    # Print ascii-safe version
    safe_text = text.encode("ascii", "ignore").decode("ascii")
    print(f"Line {idx}: {safe_text}")
