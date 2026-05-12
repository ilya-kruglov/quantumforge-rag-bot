import json
import os
import re

def load_terms_map(path='terms_map.json'):
    with open(path, 'r', encoding='utf-8') as f:
        terms = json.load(f)
    sorted_keys = sorted(terms.keys(), key=lambda x: len(x), reverse=True)
    return {k: terms[k] for k in sorted_keys}

def replace_terms(text, terms_map):
    for original, replacement in terms_map.items():
        # Если original состоит только из букв (возможно, с апострофами) – считаем однословным
        if re.fullmatch(r"[A-Za-z']+", original):
            # Границы слова, чтобы не задеть середину других слов
            pattern = re.compile(r'\b' + re.escape(original) + r'\b', re.IGNORECASE)
        else:
            # Многословные фразы – ищем как есть
            pattern = re.compile(re.escape(original), re.IGNORECASE)

        def repl(match):
            matched = match.group(0)
            if matched.isupper():
                return replacement.upper()
            elif matched[0].isupper():
                return replacement[0].upper() + replacement[1:].lower()
            else:
                return replacement.lower()
        text = pattern.sub(repl, text)
    return text

def main():
    terms_map = load_terms_map()
    raw_dir = 'raw_docs'
    out_dir = 'knowledge_base'
    os.makedirs(out_dir, exist_ok=True)
    
    for filename in sorted(os.listdir(raw_dir)):
        if not filename.endswith('.md'):
            continue
        input_path = os.path.join(raw_dir, filename)
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        new_content = replace_terms(content, terms_map)
        output_path = os.path.join(out_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Обработан: {output_path}")

if __name__ == "__main__":
    main()
