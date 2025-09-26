# app/main.py
import os
import shutil
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import whisper
from pathlib import Path

app = FastAPI()

# Allow CORS for frontend running on localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Whisper model once at startup
model = whisper.load_model("base")  # you can use "small", "medium", "large" if you want more accuracy

# Create temp directory to store uploads
TEMP_DIR = Path("temp_audio")
TEMP_DIR.mkdir(exist_ok=True)

@app.post("/api/transcribe")
async def transcribe(file: UploadFile = File(...)):
    try:
        # Save uploaded file to temp folder
        file_path = TEMP_DIR / file.filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Transcribe using Whisper
        result = model.transcribe(str(file_path))

        # Clean up uploaded file
        os.remove(file_path)

        # Prepare response
        transcription_text = result.get("text", "")

        # Here you can also implement simple summary extraction
        # For now, we'll just return the whole transcription
        response = {
            "meeting_summary": transcription_text,
            "action_items": "",  # You can add NLP to detect action items later
        }

        return response

    except Exception as e:
        return {"error": str(e)}
