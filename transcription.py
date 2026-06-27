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


os.makedirs("./transcripted",exist_ok=True)
os.makedirs("./call",exist_ok=True)


load_dotenv()
WHISPER_MODEL=os.getenv("WHISPER_MODEL")
HF_TOKEN=os.getenv("HF_TOKEN")
WHISPER_DEVICE=os.getenv("WHISPER_DEVICE")


transcription_bp= Blueprint("transcription",__name__)
@transcription_bp.route("/transcribe",methods=['POST'])

def  transcription():
    global question
    audio_file=request.files["audio"]
    question=request.form.get("question")

    file_path = os.path.join(os.getcwd(),"call", audio_file.filename)
    audio_file.save(file_path)
    # Load audio
    audio = whisperx.load_audio(f"{file_path}")


    # Translate to English
    result = model_loader.model.transcribe(
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

    toon_file_path= os.path.join(os.getcwd(), "transcripted",f"{filename}.toon" )
    transcript =  transcription_table()
    
    db.session().add(transcript)
    transcript.filename = filename
    transcript.path_in_webserver = toon_file_path
    transcript.status="processing"
    db.session().commit()

    return full_execution(toon_file_path,question)

    

    # row = transcription_table.query.get(i)
    # if():
    #     row.status = "completed"
    # else:
    #     row.status = "failed"
    # db.session.commit()