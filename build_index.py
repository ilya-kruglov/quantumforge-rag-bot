# build_index.py
import time
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# --- Параметры ---
KNOWLEDGE_DIR = "knowledge_base"        # папка с подготовленными .md файлами
INDEX_PATH = "faiss_index"              # куда сохранить индекс
CHUNK_SIZE = 500                        # символов в чанке
CHUNK_OVERLAP = 50                      # перекрытие

# --- 1. Загрузка документов ---
print("Загрузка документов...")
loader = DirectoryLoader(
    KNOWLEDGE_DIR,
    glob="*.md",
    loader_cls=TextLoader,
    loader_kwargs={"encoding": "utf-8"}
)
documents = loader.load()
print(f"Загружено документов: {len(documents)}")

# --- 2. Разбиение на чанки ---
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", " ", ""]
)
chunks = text_splitter.split_documents(documents)
print(f"Всего чанков: {len(chunks)}")

# --- 3. Эмбеддинги и индекс ---
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

print("Создание эмбеддингов и индекса FAISS...")
start_time = time.time()
vectorstore = FAISS.from_documents(chunks, embedding_model)
elapsed = time.time() - start_time
print(f"Индекс создан за {elapsed:.2f} сек.")

# --- 4. Сохранение индекса ---
vectorstore.save_local(INDEX_PATH)
print(f"Индекс сохранён в папке: {INDEX_PATH}")
