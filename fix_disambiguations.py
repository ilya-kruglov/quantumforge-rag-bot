import requests
import time
import os

def fetch_extract(page_title):
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": page_title,
        "prop": "extracts",
        "explaintext": True,
        "exsectionformat": "plain",
        "redirects": 1
    }
    headers = {"User-Agent": "QuantumForgeRAGBot/1.0"}
    resp = requests.get(url, params=params, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    pages = data["query"]["pages"]
    for page in pages.values():
        if "extract" in page:
            return page["extract"].strip()
    return None

fixes = {
    "kamino.md": "Kamino (Star Wars)",
    "droid.md": "Droid (Star Wars)"
}

for filename, title in fixes.items():
    print(f"Заменяю {filename} -> {title}")
    try:
        content = fetch_extract(title)
        if content:
            # Убираем возможную строку "For other uses, see ..."
            if content.startswith("For other uses"):
                lines = content.splitlines()
                # Пропускаем первую строку, если она начинается с "For other uses"
                if lines and lines[0].startswith("For other uses"):
                    content = "\n".join(lines[1:]).strip()
            filepath = os.path.join("raw_docs", filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {title}\n\n")
                f.write(content)
            print(f"Готово: {filename}")
        else:
            print(f"Не удалось получить содержимое для {title}")
    except Exception as e:
        print(f"Ошибка для {title}: {e}")
    time.sleep(2)  # вежливая пауза