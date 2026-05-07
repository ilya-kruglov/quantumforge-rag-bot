import requests
import re
import os
import time

topics = [
    "Hoth", "Endor (Star Wars)", "Dagobah", "Coruscant",
    "Naboo", "Alderaan", "Mustafar", "Kamino"
]

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '_', text)
    return text

def fetch_with_retries(page_title, max_retries=3):
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
    headers = {"User-Agent": "QuantumForgeRAGBot/1.0 (student project; contact: dummy@example.com)"}
    
    for attempt in range(1, max_retries + 1):
        try:
            resp = requests.get(url, params=params, headers=headers, timeout=30)
            status = resp.status_code
            if status == 200:
                data = resp.json()
                pages = data.get("query", {}).get("pages", {})
                for page_id, page_info in pages.items():
                    if page_id == "-1":
                        print(f"  Страница '{page_title}' не найдена.")
                        return None
                    extract = page_info.get("extract", "")
                    return extract.strip()
            elif status == 429:
                wait = 5 * attempt
                print(f"  429 Too Many Requests, ждём {wait} сек...")
                time.sleep(wait)
            else:
                print(f"  HTTP {status}, попытка {attempt}")
        except Exception as e:
            print(f"  Ошибка: {e}, попытка {attempt}")
            time.sleep(5 * attempt)
    return None

def main():
    for topic in topics:
        print(f"Скачиваю: {topic}")
        content = fetch_with_retries(topic)
        if content:
            filename = slugify(topic) + '.md'
            filepath = os.path.join('raw_docs', filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {topic}\n\n")
                f.write(content)
            print(f"Сохранён: {filepath}")
        else:
            print(f"Не удалось получить: {topic}")
        time.sleep(2)  # вежливая пауза между запросами

if __name__ == "__main__":
    main()
