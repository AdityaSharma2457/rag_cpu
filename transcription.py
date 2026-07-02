import whisperx
from whisperx.diarize import DiarizationPipeline
from db import transcription_table
from db_init_ import db
import uuid
import model_loader
from dotenv import load_dotenv
import os
import json
from flask import Blueprint, request
from full_execution import full_execution
from further_chat import ask_followup_question


os.makedirs("./transcripted", exist_ok=True)
os.makedirs("./call", exist_ok=True)


load_dotenv()
WHISPER_MODEL = os.getenv("WHISPER_MODEL")
HF_TOKEN = os.getenv("HF_TOKEN")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE")


transcription_bp = Blueprint("transcription", __name__)
@transcription_bp.route("/transcribe", methods=['POST'])

def transcription():

    audio_file = request.files.get("audio")
    question = request.form.get("question", "").strip()
    history_str = request.form.get("history", "[]")

    try:
        history = json.loads(history_str)
    except:
        history = []

    if not audio_file and question == "":
        return {
            "success": True,
            "answer": "Please provide a question or upload an audio file."
        }

    if audio_file:

        filename = f"{uuid.uuid4()}_{audio_file.filename}"
        file_path = os.path.join("call", filename)
        audio_file.save(file_path)
        # Load audio
        audio = whisperx.load_audio(f"{file_path}")


        # Translate to English
        result = model_loader.model.transcribe(
            audio,
            task="translate",
            language="en"
        )

        # Align words
        model_a, metadata = whisperx.load_align_model(
            language_code="en",
            device=WHISPER_DEVICE
        )

        result = whisperx.align(
            result["segments"],
            model_a,
            metadata,
            audio,
            WHISPER_DEVICE
        )

        # Diarization

        diarize_model = DiarizationPipeline(
            token=HF_TOKEN,
            device=WHISPER_DEVICE
        )

        diarize_segments = diarize_model(audio)

        result = whisperx.assign_word_speakers(
            diarize_segments,
            result
        )

        # Save toon
        filename = str(uuid.uuid4())
        with open(f"./transcripted/{filename}.toon", "w", encoding="utf-8") as f:
            f.write("conversation:\n")

            for seg in result["segments"]:
                speaker = seg.get("speaker", "UNKNOWN")
                text = seg["text"].replace("\n", " ").strip()

                f.write(f'  {speaker}: "{text}"\n')

        toon_file_path = os.path.join(os.getcwd(), "transcripted", f"{filename}.toon")
        transcript = transcription_table()

        db.session.add(transcript)
        transcript.filename = filename
        transcript.path_in_webserver = toon_file_path
        transcript.status = "processing"
        db.session.commit()
        return full_execution(toon_file_path, question, history)


@transcription_bp.route("/health", methods=['GET'])

def health():
    return {
        "status": "ok",
        "documents_indexed": 0
    }


@transcription_bp.route("/followup", methods=['POST'])

def followup():
    """
    Ask follow-up questions about a previously generated report.

    Expected JSON payload:
    {
        "report": "The full report text generated from /transcribe",
        "question": "Your follow-up question",
        "history": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]  // optional
    }
    """
    data = request.get_json()

    if not data:
        return {
            "success": False,
            "error": "Invalid JSON payload"
        }, 400

    report = data.get("report", "").strip()
    question = data.get("question", "").strip()
    history = data.get("history", [])

    if not report:
        return {
            "success": False,
            "error": "Report is required"
        }, 400

    if not question:
        return {
            "success": False,
            "error": "Question is required"
        }, 400

    try:
        answer = ask_followup_question(report, question, history)
        return {
            "success": True,
            "answer": answer
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }, 500