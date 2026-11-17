import json

with open('user_manual_annotations_exact.json', 'r', encoding='utf-8') as f:
    text = f.read()

# Clean up any potential log prefix or quotes
lines = [l.strip() for l in text.split('\n') if l.strip()]
json_str = ''
for l in lines:
    if l.startswith('"') and l.endswith('"'):
        try:
            # unescape
            l = json.loads(l)
        except Exception:
            pass
    if '{' in l:
        json_str = l
        break

parsed = json.loads(json_str)
print(f"Total entries manually filled by user: {len(parsed)}")

san_ads = []
ocu_ads = []
other_ads = []

for aid, info in parsed.items():
    note = (info.get('notes') or '').strip()
    url = (info.get('postUrl') or '').strip()
    print(f"Ad ID: {aid}")
    print(f"  Note: {repr(note)}")
    print(f"  URL:  {repr(url)}")
    
    note_lower = note.lower()
    if 'ở cữ' in note_lower or 'o cu' in note_lower:
        ocu_ads.append((aid, note, url))
    elif 'sản' in note_lower or 'san' in note_lower:
        san_ads.append((aid, note, url))
    else:
        other_ads.append((aid, note, url))

print(f"\nSummary:")
print(f"  'Sản': {len(san_ads)} ads")
for a in san_ads:
    print("    ", a)
print(f"  'Ở cữ': {len(ocu_ads)} ads")
for a in ocu_ads:
    print("    ", a)
print(f"  Other: {len(other_ads)} ads")
for a in other_ads:
    print("    ", a)

# Save clean structured file
with open('user_manual_annotations_clean.json', 'w', encoding='utf-8') as f:
    json.dump(parsed, f, ensure_ascii=False, indent=2)
print("\nSaved clean to user_manual_annotations_clean.json!")
