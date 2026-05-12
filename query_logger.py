# query_logger.py
import json
from datetime import datetime

LOG_FILE = "query_logs.jsonl"

def log_query(query_info: dict):
    """Добавляет запись в JSONL-файл."""
    record = {
        "timestamp": datetime.now().isoformat(),
        "query": query_info.get("query", ""),
        "answer": query_info.get("answer", ""),
        "status": query_info.get("status", "UNKNOWN"),
        "sources": query_info.get("sources", []),
        "num_safe_docs": query_info.get("num_safe_docs", 0),
        "answer_length": len(query_info.get("answer", ""))
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
