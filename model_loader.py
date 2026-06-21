from google import genai
from dotenv import load_dotenv
import whisperx
import os
load_dotenv()
api=os.getenv("GEMINI_API_KEY")
WHISPER_MODEL=os.getenv("WHISPER_MODEL")
WHISPER_DEVICE=os.getenv("WHISPER_DEVICE")
HF_TOKEN=os.getenv("HF_TOKEN")



client = genai.Client(
api_key=api
)
def generate_response(prompt):

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response



model = whisperx.load_model(
    WHISPER_MODEL,
    device=WHISPER_DEVICE,
    compute_type="int8"
)