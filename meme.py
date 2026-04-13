# ─────────────────────────────────────────────────────
# IMPORTS — bringing in all the tools we need
# ─────────────────────────────────────────────────────
import os           # lets us work with files and folders
import json         # lets us parse JSON responses from the LLM
import re           # lets us clean up text using patterns
import hashlib      # lets us generate unique IDs from text
import gradio as gr # lets us build the web UI
from dotenv import load_dotenv          # reads our secret API keys from .env file
import chromadb                         # our vector database
from sentence_transformers import SentenceTransformer  # converts text to vectors
from groq import Groq                   # our LLM API client
import easyocr                          # reads text from images (OCR)
from PIL import Image                   # opens image files
import imagehash                        # generates visual fingerprints of images

# ─────────────────────────────────────────────────────
# INITIALIZATION — setting up all our tools once
# ─────────────────────────────────────────────────────
load_dotenv()  # reads GROQ_API_KEY from your .env file into memory

# EasyOCR — loads the English language model for reading image text
reader = easyocr.Reader(['en'])

# Groq client — our connection to the LLM
# os.getenv() reads the API key we loaded from .env
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ChromaDB — PersistentClient saves to disk (meme_db folder)
# Next run it loads from disk — no reprocessing needed
chroma_client = chromadb.PersistentClient(path="meme_db")

# Collection — like a table in a database, stores our meme vectors
collection = chroma_client.get_or_create_collection(name="memes")

# Embedding model — converts text to a list of numbers (a vector)
# Similar meanings → similar vectors → close in mathematical space
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


# ─────────────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────────────

def generate_id(text):
    # MD5 hash — converts any text into a unique 32-character string
    # Same text always produces same ID → natural duplicate detection
    # Example: "Hello World" → "e59ff97941044f85df5297e1c302d260"
    return hashlib.md5(text.encode()).hexdigest()

def get_image_hash(path):
    # pHash (perceptual hash) — visual fingerprint of an image
    # Similar-looking images get similar hashes
    # Even if filename differs, visually identical memes are detected
    try:
        return str(imagehash.phash(Image.open(path)))
    except:
        return None  # return None if image can't be opened


# ─────────────────────────────────────────────────────
# METADATA EXTRACTION
# ─────────────────────────────────────────────────────

def extract_metadata(meme_name, ocr_text):
    # We ask the LLM to analyze the meme text and return structured JSON
    prompt = f"""
    Based on this meme filename and text, return ONLY a JSON object:

    Filename: {meme_name}
    Meme text: {ocr_text}

    Format:
    {{
        "title": "short catchy title",
        "category": "dark, wholesome, dad_joke, relatable, political, gaming, programming, animals, other",
        "keywords": ["k1", "k2"],
        "funniness": 7
    }}
    """

    try:
        # Send prompt to Groq LLM (text model)
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}]
        )

        # Extract the text response
        raw = response.choices[0].message.content

        # Clean any markdown code fences the LLM might add
        clean = raw.replace("```json", "").replace("```", "").strip()

        # Parse the JSON string into a Python dictionary
        return json.loads(clean)

    except:
        # If anything fails, return safe default values
        return {
            "title": meme_name,
            "category": "other",
            "keywords": [],
            "funniness": 5
        }


# ─────────────────────────────────────────────────────
# INGESTION — processing all memes and storing in ChromaDB
# ─────────────────────────────────────────────────────

def ingest_memes(folder_path="memes/"):
    # List all image files in the memes folder
    # Only include supported image formats, ignore other files
    files = [f for f in os.listdir(folder_path)
             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

    print(f"Found {len(files)} memes...")

    for meme in files:
        path = os.path.join(folder_path, meme)  # full file path e.g. "memes/funny.jpg"

        try:
            # OCR — extract text from the meme image
            # detail=0 means return just the text strings, not coordinates
            # " ".join() combines the list of strings into one string
            ocr_text = " ".join(reader.readtext(path, detail=0))

            # Clean the filename for use as context
            # Remove patterns like "(1)" from duplicate filenames
            clean_name = re.sub(r"\(\d+\)", "", meme)
            # Replace hyphens and underscores with spaces
            clean_name = re.sub(r"[-_]", " ", clean_name)
            # Remove the file extension (.jpg, .png etc)
            clean_name = re.sub(r"\.(jpg|jpeg|png|webp)", "", clean_name, flags=re.I).strip()

            # Combine filename + OCR text into one document
            combined = f"Meme: {clean_name}. Text: {ocr_text}"

            # Generate unique ID from content
            # Same content always gets same ID → skipped if already stored
            doc_id = generate_id(combined)

            # Generate visual hash for image deduplication
            # Two visually identical memes get the same hash
            img_hash = get_image_hash(path)

            # Skip if already in ChromaDB
            try:
                existing = collection.get(ids=[doc_id])
                if existing["ids"]:
                    print(f"⏭️ Skipping {meme} — already processed")
                    continue  # jump to next meme
            except:
                pass  # not found, proceed to add it

            # Extract metadata using LLM
            meta = extract_metadata(clean_name, ocr_text)

            # Store everything in ChromaDB
            collection.add(
                # The text document 
                documents=[combined],

                # The vectors
                embeddings=[embedding_model.encode(combined).tolist()],

                # Metadata 
                metadatas=[{
                    "path": path,                                    # file location
                    "title": meta.get("title"),                      # LLM-generated title
                    "category": meta.get("category"),                # meme category
                    "keywords": ", ".join(meta.get("keywords", [])), # keywords
                    "funniness": str(meta.get("funniness")),         # score 
                    "image_hash": img_hash                           # image hash
                }],

                # Unique ID prevents duplicate entries
                ids=[doc_id]
            )

            print(f"✅ {meme}")

        except Exception as e:
            print(f"❌ Failed {meme}: {e}")
            continue  # skip and process next meme

    print("✅ Ingestion complete!")


# ─────────────────────────────────────────────────────
# SEARCH — find relevant memes from natural language query
# ─────────────────────────────────────────────────────

def search_memes(query, n_results=5, final_k=3): # Find best 5 and finalize Top 3
    if not query.strip():
        return []  # return empty if query is blank

    # Convert the search query into a vector 
    query_embedding = embedding_model.encode(query).tolist()

    # find the n_results closest vectors
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    # These sets track what we've already shown
    # Prevents returning two visually identical or text-identical memes
    seen_text = set()
    seen_hash = set()
    gallery = []   # list of (image_path, caption) tuples for Gradio

    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):

        # Normalize text for comparison
        text_key = doc.lower().strip()
        img_hash = meta.get("image_hash")

        # Skip if we've already shown this meme (text or visual duplicate)
        if text_key in seen_text or img_hash in seen_hash:
            continue

        # Mark as seen
        seen_text.add(text_key)
        seen_hash.add(img_hash)

        # Check file still exists on disk
        path = meta.get("path")
        if not os.path.exists(path):
            continue

        # Build the caption shown under each meme in the gallery
        caption = (
            f"🎭 {meta.get('title')}\n"
            f"📂 {meta.get('category')} | 😂 {meta.get('funniness')}/10\n"
            f"🏷️ {meta.get('keywords')}"
        )

        # Add to gallery as (path, caption) tuple
        gallery.append((path, caption))

        # Stop once we have enough results
        if len(gallery) >= final_k:
            break

    return gallery  # Gradio Gallery widget accepts list of (path, caption)


# ─────────────────────────────────────────────────────
# GRADIO UI — the web interface
# ─────────────────────────────────────────────────────

def search_wrapper(query):
    # Wrapper function 
    return search_memes(query)

# Run ingestion before launching UI
# First run: processes all memes (~minutes)
# Later runs: skips everything (already in meme_db folder)
ingest_memes()

# gr.Blocks lets us build a custom layout
with gr.Blocks(title="🎭 Meme RAG") as app:
    gr.Markdown("# 🎭 Meme Search Engine")
    gr.Markdown("Search memes using natural language")

    # Text input for the search query
    query = gr.Textbox(
        placeholder="e.g. dark humor, programming memes...",
        label="Search"
    )

    # Search button
    btn = gr.Button("🔍 Search")

    gallery = gr.Gallery(
        label="Results",
        columns=3,
        height=600,
        object_fit="contain" 
    )

    btn.click(fn=search_wrapper, inputs=query, outputs=gallery)

    query.submit(fn=search_wrapper, inputs=query, outputs=gallery)

app.launch(share=True)