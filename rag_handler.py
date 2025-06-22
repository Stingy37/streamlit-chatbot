import json
import math
from openai import OpenAI
from database import save_rag_entry, load_rag_entries

client = OpenAI()  # uses your OPENAI_API_KEY

def add_rag_entry(chat_id: int, content: str):
    # build an embedding for this snippet
    resp = client.embeddings.create(model="text-embedding-ada-002", input=content)
    embedding = resp.data[0].embedding
    embedding_json = json.dumps(embedding)
    save_rag_entry(chat_id, content, embedding_json)

def get_rag_context(chat_id: int, query: str, top_k: int = 3) -> str:
    # embed query
    resp = client.embeddings.create(model="text-embedding-ada-002", input=query)
    q_emb = resp.data[0].embedding

    entries = load_rag_entries(chat_id)
    sims = []
    for e in entries:
        emb = json.loads(e["embedding"])
        dot = sum(a*b for a,b in zip(q_emb, emb))
        norm_q = math.sqrt(sum(a*a for a in q_emb))
        norm_e = math.sqrt(sum(b*b for b in emb))
        score = dot / (norm_q*norm_e + 1e-9)
        sims.append((score, e["content"]))

    # pick top_k
    sims.sort(key=lambda x: x[0], reverse=True)
    top_snippets = [txt for _, txt in sims[:top_k]]
    return "\n\n".join(top_snippets)