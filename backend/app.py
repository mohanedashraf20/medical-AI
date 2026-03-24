from flask import Flask, request, jsonify
from openai import OpenAI
import PyPDF2
import numpy as np
import faiss
import re

app = Flask(__name__)
client = OpenAI(api_key="YOUR_API_KEY")

chat_history = []

def read_pdf(file):
    text = ""
    pdf = PyPDF2.PdfReader(file)
    for page in pdf.pages:
        text += page.extract_text() + "\n"
    return text

def split_text(text, chunk_size=500):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def get_embedding(text):
    res = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return res.data[0].embedding

text = read_pdf("bylaws.pdf")
chunks = split_text(text)

embeddings = [get_embedding(chunk) for chunk in chunks]

dim = len(embeddings[0])
index = faiss.IndexFlatL2(dim)
index.add(np.array(embeddings).astype("float32"))

def search(query, k=3):
    q_emb = np.array([get_embedding(query)]).astype("float32")
    D, I = index.search(q_emb, k)
    return [chunks[i] for i in I[0]]

def extract_article(text):
    match = re.search(r'Article\s*\(?\d+\)?', text)
    return match.group() if match else "Unknown Article"

def ask_ai(question):
    results = search(question)
    context = "\n".join(results)

    messages = [
        {"role": "system", "content": "Answer ONLY from this context:\n" + context}
    ]

    messages += chat_history
    messages.append({"role": "user", "content": question})

    response = client.chat.completions.create(
        model="gpt-5.3",
        messages=messages
    )

    answer = response.choices[0].message.content
    article = extract_article(context)

    chat_history.append({"role": "user", "content": question})
    chat_history.append({"role": "assistant", "content": answer})

    return answer, article, results[0]

@app.route("/ask", methods=["POST"])
def ask():
    question = request.json["question"]

    answer, article, source = ask_ai(question)

    return jsonify({
        "answer": answer,
        "article": article,
        "source": source
    })

app.run(debug=True)
