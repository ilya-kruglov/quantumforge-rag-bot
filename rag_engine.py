import torch
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import string

INDEX_PATH = "faiss_index"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
LOCAL_LLM_NAME = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"

# ------------------- Загрузка индекса и LLM -------------------
embedding_model = HuggingFaceEmbeddings(
    model_name=EMBEDDING_MODEL_NAME,
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)
vectorstore = FAISS.load_local(INDEX_PATH, embedding_model, allow_dangerous_deserialization=True)

print("Загрузка TinyLlama...")
tokenizer = AutoTokenizer.from_pretrained(LOCAL_LLM_NAME)
model = AutoModelForCausalLM.from_pretrained(
    LOCAL_LLM_NAME,
    dtype=torch.float32,
    device_map="cpu",
    low_cpu_mem_usage=True
)
text_generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=250,
    do_sample=False,
    temperature=None
)
print("Готово.")

# ------------------- Few‑shot примеры (формат ответа) -------------------
FEW_SHOT = """Example 1:
Question: Who trained Jax Solara?
Context: Jax Solara was trained by Zan Varos and later by Oron.
Answer: Jax Solara was trained by Zan Varos and later by Oron.

Example 2:
Question: What is the Void Core?
Context: The Void Core is a massive space station capable of destroying entire planets, built by the Dominion of Iron Will.
Answer: The Void Core is a massive space station built by the Dominion of Iron Will.

Example 3:
Question: What is the capital of France?
Context: France's capital is Paris.
Answer: I don't know.
"""

SYSTEM_PROMPT = """You are a knowledge base assistant for the "Celestial Chronicles" universe.
Answer the question using ONLY the provided context. Do not use outside knowledge.
Provide a concise answer. If the context does not contain the answer, say exactly "I don't know."
"""

def generate_answer(query, docs):
    """Отправляет промпт в LLM и возвращает чистый ответ."""
    context = "\n\n".join([f"From {doc.metadata['source']}:\n{doc.page_content}" for doc in docs])
    prompt = f"{FEW_SHOT}\n\n{SYSTEM_PROMPT}\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"
    result = text_generator(prompt)
    generated = result[0]['generated_text']
    # Извлекаем всё после последнего "Answer:"
    if "Answer:" in generated:
        answer = generated.split("Answer:")[-1].strip()
    else:
        answer = generated.strip()
    # Обрезаем по первому переводу строки (остальное – мусор)
    answer = answer.split('\n')[0].strip()
    return answer

def is_answer_valid(answer, docs, min_shared=3):
    """Проверяет, что ответ основан на контексте."""
    if "i don't know" in answer.lower():
        return True
    context_text = " ".join([doc.page_content for doc in docs]).lower()
    translator = str.maketrans('', '', string.punctuation)
    context_text = context_text.translate(translator)
    answer_text = answer.lower().translate(translator)
    context_words = set(context_text.split())
    answer_words = set(answer_text.split())
    shared = context_words & answer_words
    return len(shared) >= min_shared

def query_rag(user_query, k=4):
    docs = vectorstore.similarity_search(user_query, k=k)
    if not docs:
        return "Step 1: Received question: *" + user_query + "*\nStep 2: No relevant documents found in the knowledge base.\nFinal answer: I don't know."

    # --- Генерация ответа LLM (только финальный ответ) ---
    raw_answer = generate_answer(user_query, docs)

    # Проверка на галлюцинацию
    if not is_answer_valid(raw_answer, docs):
        raw_answer = "I don't know."

    # --- Строим цепочку рассуждений (CoT) программно ---
    sources = list(set(doc.metadata.get('source', 'unknown') for doc in docs))
    cot_steps = []
    cot_steps.append(f"Step 1: Received question: *{user_query}*")
    cot_steps.append(f"Step 2: Searched the knowledge base and found {len(docs)} relevant chunks from documents: {', '.join(sources)}.")
    # Покажем небольшой отрывок из самого близкого чанка (max 200 символов)
    snippet = docs[0].page_content.strip().replace('\n', ' ')[:200]
    cot_steps.append(f"Step 3: The closest snippet mentions: \"{snippet}...\"")
    if raw_answer.strip().lower() == "i don't know." or raw_answer.strip().lower() == "i don't know":
        cot_steps.append("Step 4: However, the context does not contain a clear answer.")
    else:
        cot_steps.append(f"Step 4: Based on this information, the answer is: {raw_answer}")
    cot_steps.append(f"Final answer: {raw_answer}")

    return "\n".join(cot_steps)
