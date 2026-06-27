import whisperx
from whisperx.diarize import DiarizationPipeline
from db import transcription_table
from db_init_ import db
import uuid 
import model_loader
from dotenv import load_dotenv
import os
from flask import Blueprint,request
from full_execution import full_execution

from flask import jsonify


os.makedirs("./transcripted",exist_ok=True)
os.makedirs("./call",exist_ok=True)


load_dotenv()
WHISPER_MODEL=os.getenv("WHISPER_MODEL")
HF_TOKEN=os.getenv("HF_TOKEN")
WHISPER_DEVICE=os.getenv("WHISPER_DEVICE")


transcription_bp= Blueprint("transcription",__name__)

@transcription_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "documents_indexed": 0
    })
    
    
@transcription_bp.route("/query", methods=["POST"])
def query():
    return jsonify({
        "success": True,
        "answer": "Test answer from backend",
        "sources": [],
        "tokens_used": {
            "total": 0
        }
    })


@transcription_bp.route("/transcribe",methods=['POST'])

def  transcription():
    global question
    audio_file=request.files["audio"]
    question=request.form.get("question")

    file_path = os.path.join(os.getcwd(),"call", audio_file.filename)
    audio_file.save(file_path)
    
   
    
    print("1. Audio received")
    
    # Load audio
    audio = whisperx.load_audio(f"{file_path}")

    print("2. Audio loaded")

    # Translate to English
    result = model_loader.model.transcribe(
        audio,
        task="translate"
    )
    
    print("3. Transcription completed")

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

    print("4. Alignment completed")
    
    # Diarization
    
    print("5. Before diarization")
    diarize_model = DiarizationPipeline(
        token=HF_TOKEN,
        device=WHISPER_DEVICE
    )
    print("6. Diarization model loaded")

    diarize_segments = diarize_model(audio)
    print("5. Diarization completed")

    result = whisperx.assign_word_speakers(
        diarize_segments,
        result
    )
    
    print("5. Diarization completed")

    # Save toon
    filename=str(uuid.uuid4())
    with open(f"./transcripted/{filename}.toon", "w", encoding="utf-8") as f:
        f.write("conversation:\n")

        for seg in result["segments"]:
            speaker = seg.get("speaker", "UNKNOWN")
            text = seg["text"].replace("\n", " ").strip()

            f.write(f'  {speaker}: "{text}"\n')

    toon_file_path= os.path.join(os.getcwd(), "transcripted",f"{filename}.toon" )
    transcript =  transcription_table()
    
    print("6. TOON file saved")
    
    db.session().add(transcript)
    transcript.filename = filename
    transcript.path_in_webserver = toon_file_path
    transcript.status="processing"
    db.session().commit()

    return full_execution(toon_file_path,question)

    

@transcription_bp.route("/health",methods=['GET'])

def health():
    return {
        "status":"ok",
        "documents_indexed" :0
    }

    # row = transcription_table.query.get(i)
    # if():
    #     row.status = "completed"
    # else:
    #     row.status = "failed"
    # db.session.commit()