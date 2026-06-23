import whisperx
from whisperx.diarize import DiarizationPipeline
from db import transcription_table,db
import uuid 
from dotenv import load_dotenv
import os
<<<<<<< Updated upstream
from flask import Blueprint
=======
from flask import Blueprint,request
from full_execution import full_execution

from flask import jsonify

os.makedirs("./transcripted",exist_ok=True)
os.makedirs("./call",exist_ok=True)

>>>>>>> Stashed changes

load_dotenv()
transcription_bp= Blueprint("transcription",__name__)
<<<<<<< Updated upstream
@transcription_bp.route("/<audio_file>")

def  transcription(audio_file):
    # Load model
    WHISPER_MODEL=os.getenv("WHISPER_MODEL")
    WHISPER_DEVICE=os.getenv("WHISPER_DEVICE")
    HF_TOKEN=os.getenv("HF_TOKEN")
=======



@transcription_bp.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "documents_indexed": 0
    })

@transcription_bp.route("/transcribe",methods=['POST'])
def  transcription():
    audio_file=request.files["audio"]
    question=request.form.get("question")
    file_path = os.path.join(os.getcwd(),"call", audio_file.filename)
    audio_file.save(file_path)
    # Load audio
    audio = whisperx.load_audio(f"{file_path}")
>>>>>>> Stashed changes

    model = whisperx.load_model(
        WHISPER_MODEL,
        device=WHISPER_DEVICE,
        # compute_type="float16"
        compute_type="int8"
    )

    # # Load audio
    # audio = whisperx.load_audio(f"{audio_file}")
    
    audio_path = os.path.join(
        os.getcwd(),"call",audio_file
        )
    print("Loading:", audio_path)
    audio = whisperx.load_audio(audio_path)

    # Translate to English
    result = model.transcribe(
        audio,
        task="translate"
    )
    print("Transcription complete")
    
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
    print("Alignment complete")

    # Diarization
    
    print("Starting diarization")
    diarize_model = DiarizationPipeline(
        token=HF_TOKEN,
        device=WHISPER_DEVICE
    )

    diarize_segments = diarize_model(audio)

    result = whisperx.assign_word_speakers(
        diarize_segments,
        result
    )
    print("Diarization complete")

    # Save toon
    # filename=str(uuid.uuid6())
    filename=str(uuid.uuid4())
    os.makedirs("transcripted", exist_ok=True)
    with open(f"./transcripted/{filename}.toon", "w", encoding="utf-8") as f:
        f.write("conversation:\n")

        for seg in result["segments"]:
            speaker = seg.get("speaker", "UNKNOWN")
            text = seg["text"].replace("\n", " ").strip()

            f.write(f'  {speaker}: "{text}"\n')

    transcript =  transcription_table()
    
    # db.session.add(transcript)
    transcript.filename = filename
    transcript.path_in_webserver = f"./transcripted/{filename}.toon" 
    transcript.status="processing"
<<<<<<< Updated upstream
    
    db.session.add(transcript)
    db.session.commit()
    print("Transcript saved successfully")
    print("Finished processing")
    
    return {
        "status": "success",
        "filename": filename
        }
=======
    db.session().commit()

    full_execution(toon_file_path,question)

    # return 0
    return jsonify({
    "success": True,
    "message": "Transcription completed"
})


>>>>>>> Stashed changes


    # row = transcription_table.query.get(i)
    # if():
    #     row.status = "completed"
    # else:
    #     row.status = "failed"
    # db.session.commit()


