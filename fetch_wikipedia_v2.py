import requests
import re
import os
import json

# Проверенные названия статей (35 штук), которые точно существуют в Википедии
topics = [
    "Darth Vader", "Luke Skywalker", "Leia Organa", "Han Solo", "Yoda",
    "Obi-Wan Kenobi", "Palpatine", "Chewbacca", "R2-D2", "C-3PO",
    "Tatooine", "Hoth", "Endor (Star Wars)", "Dagobah", "Coruscant",
    "Naboo", "Alderaan", "Mustafar", "Kamino",
    "Death Star", "Lightsaber", "Millennium Falcon",
    "Technology in Star Wars",   # замена неоднозначного Hyperdrive
    "AT-AT", "X-wing fighter",
    "Clone Wars (Star Wars)", "Galactic Empire (Star Wars)",
    "Rebel Alliance", "The Force", "Jedi", "Sith",
    "Yavin",          # включает Битву при Явине
    "Order 66",       # существует напрямую
    "Wookiee", "Droid"
]

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '_', text)
    return text

def fetch_wikipedia_extract(page_title):
    """
    Получает plain-text содержимое страницы через Wikipedia REST API.
    """
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "format": "json",
        "titles": page_title,
        "prop": "extracts",
        "explaintext": True,
        "exsectionformat": "plain",
        "redirects": 1  # автоматически следовать перенаправлениям
    }
    headers = {"User-Agent": "QuantumForgeRAGBot/1.0"}
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()
    pages = data.get("query", {}).get("pages", {})
    for page_id, page_info in pages.items():
        if page_id == "-1":  # страница не найдена
            return None
        extract = page_info.get("extract", "")
        return extract.strip()
    return None

def main():
    os.makedirs('raw_docs', exist_ok=True)
    for topic in topics:
        print(f"Скачиваю: {topic}")
        try:
            content = fetch_wikipedia_extract(topic)
            if not content:
                print(f"Не удалось найти страницу: {topic}")
                continue
            filename = slugify(topic) + '.md'
            filepath = os.path.join('raw_docs', filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"# {topic}\n\n")
                f.write(content)
            print(f"Сохранён: {filepath}")
        except Exception as e:
            print(f"Ошибка для {topic}: {e}")

if __name__ == "__main__":
    main()
