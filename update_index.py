import os
import time
from datetime import datetime
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

INCOMING_DIR = "incoming_docs"
INDEX_PATH = "faiss_index"
PROCESSED_FILE = "processed.txt"
LOG_FILE = "update.log"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

def log(message: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def load_processed():
    if not os.path.exists(PROCESSED_FILE):
        return set()
    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

def save_processed(file_set):
    with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
        for filename in sorted(file_set):
            f.write(filename + "\n")

def main():
    log("=== Запуск обновления индекса ===")
    start_time = time.time()

    if not os.path.exists(INDEX_PATH):
        log("Ошибка: индекс не найден. Сначала выполните build_index.py")
        return

    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    vectorstore = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)

    processed = load_processed()
    incoming_files = []
    if os.path.exists(INCOMING_DIR):
        for fname in os.listdir(INCOMING_DIR):
            if fname.endswith(".md") and fname not in processed:
                incoming_files.append(fname)
    else:
        os.makedirs(INCOMING_DIR, exist_ok=True)
        log(f"Создана папка {INCOMING_DIR}")

    if not incoming_files:
        log("Новых документов не обнаружено.")
        log(f"Обновление завершено за {time.time() - start_time:.2f} сек.")
        return

    log(f"Найдено новых документов: {len(incoming_files)}")

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    total_added = 0
    for fname in incoming_files:
        filepath = os.path.join(INCOMING_DIR, fname)
        try:
            loader = TextLoader(filepath, encoding="utf-8")
            docs = loader.load()
            chunks = text_splitter.split_documents(docs)
            if not chunks:
                log(f"  {fname}: нет чанков, пропущен")
                continue
            vectorstore.add_documents(chunks)
            total_added += len(chunks)
            processed.add(fname)
            log(f"  {fname}: добавлено {len(chunks)} чанков")
        except Exception as e:
            log(f"  Ошибка при обработке {fname}: {e}")

    vectorstore.save_local(INDEX_PATH)
    save_processed(processed)

    elapsed = time.time() - start_time
    log(f"Всего добавлено чанков: {total_added}")
    log(f"Размер индекса (примерно): {vectorstore.index.ntotal} векторов")
    log(f"Обновление завершено за {elapsed:.2f} сек.\n")

if __name__ == "__main__":
    main()
