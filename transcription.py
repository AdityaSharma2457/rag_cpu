import whisperx
from db import transcription_table,history_table
from db_init_ import db
import uuid
import model_loader
from dotenv import load_dotenv
import os
import json
from flask import Blueprint, request
from sqlalchemy.orm.attributes import flag_modified
from full_execution import full_execution
from further_chat import ask_followup_question


os.makedirs("./transcripted", exist_ok=True)
os.makedirs("./call", exist_ok=True)


load_dotenv()
WHISPER_MODEL = os.getenv("WHISPER_MODEL")
HF_TOKEN = os.getenv("HF_TOKEN")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE")


transcription_bp = Blueprint("transcription", __name__)


def normalize_history(history_value):
    if isinstance(history_value, str):
        history_value = json.loads(history_value)
    if not history_value or "history" not in history_value:
        return {"history": []}
    return history_value


def session_title(history_value):
    try:
        data = normalize_history(history_value)
        for item in data["history"]:
            question = str(item.get("question", "")).strip()
            if question:
                return question[:80]
    except Exception:
        pass
    return "Untitled analysis"


@transcription_bp.route("/transcribe", methods=['POST'])

def transcription():
    session_id = request.form.get("session_id", "").strip()
    audio_file = request.files.get("audio")
    question = request.form.get("question", "").strip()

    if not session_id:
        return {
            "success": False,
            "error": "session_id is required"
        }, 400


    if not audio_file and question == "":
        return {
            "success": False,
            "error": "Please provide a question and upload an audio file."
        }, 400

    if not audio_file:
        return {
            "success": False,
            "error": "Please upload an audio file for a new analysis."
        }, 400

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


        result = whisperx.align(
            result["segments"],
            model_loader.model_a,
            model_loader.metadata,
            audio,
            WHISPER_DEVICE
        )

        # Diarization
        diarize_segments = model_loader.diarize_model(audio)

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
        transcript = db.session.get(transcription_table, session_id)
        if transcript is None:
            transcript = transcription_table()
            transcript.session_id=session_id
            db.session.add(transcript)

        transcript.path_in_webserver = toon_file_path
        transcript.report_path_in_webserver="null"
        transcript.status = "processing"
        db.session.commit()
        return full_execution(session_id,toon_file_path, question)


@transcription_bp.route("/health", methods=['GET'])

def health():
    return {
        "status": "ok",
        "documents_indexed": 0
    }


@transcription_bp.route("/sessions", methods=['GET'])
def sessions():
    histories = history_table.query.order_by(history_table.updated_at.desc()).all()
    transcript_rows = {
        row.session_id: row
        for row in transcription_table.query.filter(
            transcription_table.session_id.in_([h.session_id for h in histories])
        ).all()
    } if histories else {}

    return {
        "success": True,
        "sessions": [
            {
                "session_id": history.session_id,
                "title": session_title(history.history),
                "updated_at": history.updated_at.isoformat() if history.updated_at else None,
                "status": transcript_rows.get(history.session_id).status if transcript_rows.get(history.session_id) else "completed"
            }
            for history in histories
        ]
    }


@transcription_bp.route("/sessions/<session_id>", methods=['GET'])
def session_history(session_id):
    history = db.session.get(history_table, session_id)
    if history is None:
        return {
            "success": False,
            "error": "History not found"
        }, 404

    transcript = db.session.get(transcription_table, session_id)
    return {
        "success": True,
        "session_id": session_id,
        "history": normalize_history(history.history),
        "status": transcript.status if transcript else "completed",
        "updated_at": history.updated_at.isoformat() if history.updated_at else None
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

    question = data.get("question", "").strip()
    session_id = str(data.get("session_id", "")).strip()
    if not question:
        return {
            "success": False,
            "error": "Question is required"
        }, 400

    if not session_id:
        return {
            "success": False,
            "error": "session_id is required"
        }, 400

    try:
        history = db.session.get(history_table, session_id)
        if history is None:
            return {
                "success": False,
                "error": "History not found"
            }, 404

        answer = ask_followup_question( question,session_id)
        if (answer):
            data = normalize_history(history.history)

            data["history"].append({
            "question": question,
            "response": answer
            })
            history.history = data
            flag_modified(history, "history")

            db.session.commit()
        return {
            "success": True,
            "answer": answer
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }, 500
