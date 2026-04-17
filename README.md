
# 🎭 Meme RAG

> 🔍 Search memes using natural language — powered by RAG, EasyOCR, ChromaDB & Groq

🔗 **Live Demo:** [https://syednajum-meme-rag.hf.space/](https://syednajum-meme-rag.hf.space/)

---

## ⚙️ Getting Started

### 1. Prerequisites

* Python **3.9+**
* Groq API Key
  👉 [https://console.groq.com/](https://console.groq.com/)

---

### 2. Installation

```bash
git clone <your-repo-url>
cd meme-rag

pip install os json re hashlib gradio python-dotenv chromadb sentence-transformers groq easyocr Pillow imagehash
```

---

### 3. Configuration

Create a `.env` file:

```env
GROQ_API_KEY=your_api_key_here
```

---

### 4. Setup Memes

Create a folder:

```bash
memes/
```

Add your meme images (`.jpg`, `.png`, `.webp`).

---

## 🎮 Usage

Run the application:

```bash
python meme.py
```

### First Run

* Processes all memes
* Performs OCR + LLM metadata generation
* Stores embeddings

### Subsequent Runs

* Skips already processed memes using stored IDs

---

### 🔎 Searching

Open the Gradio interface:

```
http://127.0.0.1:7860
```

Start searching using natural language!

---

## 🧾 Example Metadata

```json
{
    "title": "The Infinite Loop Struggle",
    "category": "programming",
    "keywords": ["coding", "loop", "frustration"],
    "funniness": 8
}
```

---

## 🧠 Tech Stack

* **LLM:** Llama 3 (Groq API)
* **Embeddings:** Sentence Transformers
* **Vector DB:** ChromaDB
* **OCR:** EasyOCR
* **UI:** Gradio
* **Image Processing:** Pillow + ImageHash
