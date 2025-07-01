import json
from pathlib import Path

# Input and output file paths
SCRAPED_FILE = "pragyan_nicsi_filtered_data.json"
OUTPUT_FILE = "company_data.json"

# Load raw scraped content
with open(SCRAPED_FILE, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

# Convert to structured format
company_data = []
for url, content in raw_data.items():
    if not content.strip():
        continue
    entry = {
        "title": url,        # or extract meaningful title from content if needed
        "content": content.strip()
    }
    company_data.append(entry)

# Save as company_data.json
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(company_data, f, ensure_ascii=False, indent=2)

print(f"✅ Converted {len(company_data)} pages into company_data.json")
