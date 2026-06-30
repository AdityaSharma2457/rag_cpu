from flask import Blueprint, jsonify, request
from transcription import transcription
from chat_pipeline import chat_pipeline
import json



controller_bp = Blueprint("check_msg", __name__)
@controller_bp.route("/", methods=['POST'])

def check_msg():
    audio_file = request.files["audio"]
    question = request.form.get("question")
    if audio_file:
        return transcription(audio_file, question)
    if question:
        return chat_pipeline(question)
    return jsonify({
        "error" : "Either audio file or question is required"
    }, 400)



@controller_bp.route("/health",methods=['GET'])

def health():
    return {
        "status":"ok",
        "documents_indexed" :0
    }