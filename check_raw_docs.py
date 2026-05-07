import os

raw_dir = 'raw_docs'
for filename in sorted(os.listdir(raw_dir)):
    if not filename.endswith('.md'):
        continue
    filepath = os.path.join(raw_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        first_lines = ''.join([f.readline() for _ in range(5)])
    if 'may refer to:' in first_lines or 'disambiguation' in first_lines.lower():
        print(f"Возможная неоднозначность: {filename}")