# main.py
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
import requests
import base64
import json

app = FastAPI(title="Multi-Modal Assistant API")

# Allow frontend (Streamlit) to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Function to call Ollama API
def call_ollama(payload):
    try:
        response = requests.post("http://localhost:11434/api/generate", json=payload, stream=True)
        response.raise_for_status()
    except requests.RequestException as e:
        return f"Request failed: {e}"

    answer_text = ""
    debug_output = []

    for line in response.iter_lines():
        if line:
            try:
                obj = json.loads(line.decode("utf-8"))
                debug_output.append(obj)
                if "response" in obj and obj["response"]:
                    answer_text += obj["response"]
            except Exception as e:
                debug_output.append({"error": str(e), "raw": line.decode("utf-8")})

    if not answer_text.strip():
        return f"No answer. Debug: {debug_output[:3]}"

    return answer_text.strip()


@app.post("/multimodal-query")
async def multimodal_query(
    question: str = Form(None),
    image: UploadFile = None
):
    if not question and not image:
        return {"error": "Please provide a question or an image."}

    image_base64 = None
    if image:
        try:
            image_bytes = await image.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
        except Exception as e:
            return {"error": f"Failed to process image: {e}"}

    payload = {
        "model": "llava",  # Replace with your installed vision model
        "prompt": question if question else "",
        "images": [image_base64] if image_base64 else []
    }

    result = call_ollama(payload)
    return {"response": result}
