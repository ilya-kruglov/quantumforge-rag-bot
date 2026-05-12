# evaluate.py
import json
from rag_engine import query_rag_raw
from query_logger import log_query


def load_golden_questions(path="golden_questions.json"):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    questions = load_golden_questions()
    stats = {"total": len(questions), "correct": 0, "wrong": 0, "details": []}

    for item in questions:
        q = item["question"]
        expected = item.get("expected_status", "ANSWER_FOUND")
        result = query_rag_raw(q)
        log_query(result)

        actual_status = result["status"]
        correct = (actual_status == expected)

        # Дополнительная проверка ключевых слов, если заданы
        if correct and "keywords" in item:
            answer_lower = result["answer"].lower()
            if not all(kw.lower() in answer_lower for kw in item["keywords"]):
                correct = False

        stats["details"].append({
            "question": q,
            "expected": expected,
            "actual": actual_status,
            "correct": correct,
            "answer": result["answer"][:100] + "..." if len(result["answer"]) > 100 else result["answer"]
        })

        if correct:
            stats["correct"] += 1
        else:
            stats["wrong"] += 1

    # Вывод сводки
    print("\n===== РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ =====")
    for d in stats["details"]:
        status = "✅" if d["correct"] else "❌"
        print(f"{status} {d['question']}")
        print(f"   Expected: {d['expected']}, Actual: {d['actual']}")
        print(f"   Answer snippet: {d['answer']}\n")

    print(f"Всего вопросов: {stats['total']}")
    print(f"Корректных: {stats['correct']}")
    print(f"Ошибочных: {stats['wrong']}")

    # Сохраняем сводку в файл для отчёта
    with open("evaluation_report.json", "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
