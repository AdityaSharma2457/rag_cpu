import whisperx
from whisperx.diarize import DiarizationPipeline
import db
import uuid 
from dotenv import load_dotenv
import os

load_dotenv()

@app.route()

def  transcription(audio_file):
    device = "cuda"
    # Load model
    model = whisperx.load_model(
        "large-v3",
        device=device,
        compute_type="float16"
    )

    # Load audio
    audio = whisperx.load_audio(f"{audio_file}")

    # Translate to English
    result = model.transcribe(
        audio,
        task="translate"
    )

    # Align words
    model_a, metadata = whisperx.load_align_model(
        language_code="en",
        device=device
    )

    result = whisperx.align(
        result["segments"],
        model_a,
        metadata,
        audio,
        device
    )

    # Diarization
    # HF_TOKEN = f"{HF_TOKEN}"
    
    HF_TOKEN = os.getenv("HF_TOKEN")

    diarize_model = DiarizationPipeline(
        token=HF_TOKEN,
        device=device
    )

    diarize_segments = diarize_model(audio)

    result = whisperx.assign_word_speakers(
        diarize_segments,
        result
    )

    # Save toon
    filename=str(uuid.uuid6())
    with open(f"./transcripted/{filename}.toon", "w", encoding="utf-8") as f:
        f.write("conversation:\n")

    for seg in result["segments"]:
        speaker = seg.get("speaker", "UNKNOWN")
        text = seg["text"].replace("\n", " ").strip()

        f.write(f'  {speaker}: "{text}"\n')

    transcript =  transcription()
    
    db.session().add(transcript)
    transcript.filename = filename
    transcript.path_in_webserver = f"./transcripted/{filename}.toon" 
    transcript.status="processing"
    db.session().commit()



    row = transcription.query.get(i)
    if():
        row.status = "completed"
    else:
        row.status = "failed"
    db.session.commit()


