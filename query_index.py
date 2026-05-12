# query_index.py
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

INDEX_PATH = "faiss_index"

# Загружаем индекс
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)
vectorstore = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)

# Задайте тестовый запрос
query = "Who is Xarn Velgor and what is his relationship to Jax Solara?"
docs = vectorstore.similarity_search(query, k=3)

for i, doc in enumerate(docs):
    print(f"\n--- Результат #{i+1} ---")
    print(f"Источник: {doc.metadata.get('source', 'unknown')}")
    print(doc.page_content[:500])
