
# 🎭 Meme RAG

> 🔍 Search memes using natural language — powered by RAG, EasyOCR, ChromaDB & Groq

🔗 **Live Demo:** [https://syednajum-meme-rag.hf.space/](https://syednajum-meme-rag.hf.space/)

---

## 🚀 Overview

**Meme RAG** is an intelligent, AI-powered search engine for your local meme collection.
It uses a **Retrieval-Augmented Generation (RAG)** pipeline to:

* Extract text from memes using OCR
* Generate meaningful metadata using LLMs
* Enable **semantic search** using natural language

Instead of searching by filename, you can search by **meaning, context, or vibe**.

---

## ✨ Features

### 🔍 Semantic Search

Search memes using natural language:

* *"coding at 2 AM"*
* *"frustrated office worker"*

---

### 🧠 AI-Powered Tagging

* Uses **Llama 3 (via Groq)**
* Generates:

  * Titles
  * Categories
  * Keywords
  * Funniness score

---

### 👁️ OCR (Optical Character Recognition)

* Powered by **EasyOCR**
* Extracts text directly from meme images

---

### 🛡️ Duplicate Prevention

* **Text-based:** MD5 hashing
* **Visual-based:** Perceptual hashing (pHash)

---

### 💾 Persistent Storage

* Uses **ChromaDB**
* Keeps your meme embeddings stored across sessions

---

### 🌐 Interactive UI

* Built with **Gradio**
* Clean and user-friendly meme search interface

---

## 🏗️ Technical Architecture

### 1. Ingestion

* Scans the `memes/` folder for images

### 2. Extraction

* **Text:** EasyOCR extracts captions
* **Visuals:** ImageHash generates fingerprint

### 3. Analysis

* Sends OCR text + filename to **Groq API**
* Generates structured metadata (JSON)

### 4. Vectorization

* Uses `all-MiniLM-L6-v2`
* Converts text → **384-dimensional embeddings**

### 5. Storage

* Stored in **ChromaDB** with metadata

### 6. Retrieval

* User query → embedding
* Compared using **cosine similarity**
* Returns most relevant memes

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
python main.py
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
