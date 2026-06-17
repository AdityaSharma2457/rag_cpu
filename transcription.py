import whisperx
from whisperx.diarize import DiarizationPipeline
from db import transcription_table
from db_init_ import db
import uuid 
from dotenv import load_dotenv
import os
from flask import Blueprint

load_dotenv()
os.makedirs("./transcripted",exist_ok=True)


transcription_bp= Blueprint("transcription",__name__)
@transcription_bp.route("/<audio_file>")

def  transcription(audio_file):
    # Load model
    WHISPER_MODEL=os.getenv("WHISPER_MODEL")
    WHISPER_DEVICE=os.getenv("WHISPER_DEVICE")
    HF_TOKEN=os.getenv("HF_TOKEN")

    model = whisperx.load_model(
        WHISPER_MODEL,
        device=WHISPER_DEVICE,
        compute_type="int8"
    )
    audio_path = os.path.join(os.getcwd(), "call", audio_file)
    # Load audio
    audio = whisperx.load_audio(f"{audio_path}")

    # Translate to English
    result = model.transcribe(
        audio,
        task="translate"
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
    filename=str(uuid.uuid4())
    with open(f"./transcripted/{filename}.toon", "w", encoding="utf-8") as f:
        f.write("conversation:\n")

        for seg in result["segments"]:
            speaker = seg.get("speaker", "UNKNOWN")
            text = seg["text"].replace("\n", " ").strip()

            f.write(f'  {speaker}: "{text}"\n')

    transcript =  transcription_table()
    
    db.session().add(transcript)
    transcript.filename = filename
    transcript.path_in_webserver = f"./transcripted/{filename}.toon" 
    transcript.status="processing"
    db.session().commit()


    # row = transcription_table.query.get(i)
    # if():
    #     row.status = "completed"
    # else:
    #     row.status = "failed"
    # db.session.commit()


