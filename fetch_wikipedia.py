import wikipedia
import re
import os

# Список статей (названия на английском, как в Википедии)
topics = [
    "Darth Vader", "Luke Skywalker", "Princess Leia", "Han Solo", "Yoda",
    "Obi-Wan Kenobi", "Palpatine", "Chewbacca", "R2-D2", "C-3PO",
    "Tatooine", "Hoth", "Endor (Star Wars)", "Dagobah", "Coruscant",
    "Naboo", "Alderaan", "Mustafar", "Kamino",
    "Death Star", "Lightsaber", "Millennium Falcon", "Hyperdrive",
    "AT-AT", "X-wing fighter",
    "Clone Wars (Star Wars)", "Galactic Empire (Star Wars)",
    "Rebel Alliance", "The Force", "Jedi", "Sith",
    "Battle of Yavin", "Order 66 (Star Wars)", "Wookiee", "Droid (Star Wars)"
]

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '_', text)
    return text

def main():
    os.makedirs('raw_docs', exist_ok=True)
    for topic in topics:
        try:
            print(f"Скачиваю: {topic}")
            page = wikipedia.page(topic, auto_suggest=False)
            content = page.content
            # Убираем пустые строки в начале/конце
            content = content.strip()
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
