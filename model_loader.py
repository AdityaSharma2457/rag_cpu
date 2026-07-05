from dotenv import load_dotenv
import whisperx
import os
from whisperx.diarize import DiarizationPipeline

from openai import OpenAI
load_dotenv()





client = None
model = None
diarize_model = None
model_a = None
metadata = None



api=os.getenv("GEMINI_API_KEY")
WHISPER_MODEL=os.getenv("WHISPER_MODEL")
WHISPER_DEVICE=os.getenv("WHISPER_DEVICE")
HF_TOKEN=os.getenv("HF_TOKEN")



def load_models():
    global client,model,diarize_model,model_a,metadata

    if client is None:
        print("Loading OpenAI client...💡")
        client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = os.getenv('NEMOTRON')
)
    if model is None:
        print("Loading Whisper model...💡")
        model = whisperx.load_model(
        WHISPER_MODEL,
        device=WHISPER_DEVICE,
        compute_type="int8"
    )
    if diarize_model is None:
        print("Loading Diarization model...💡")
        diarize_model = DiarizationPipeline(
            token=HF_TOKEN,
            device=WHISPER_DEVICE
        )
    if model_a is None or metadata is None:
        print("Loading alignment model...💡")
        model_a, metadata = whisperx.load_align_model(
            language_code="en",
            device=WHISPER_DEVICE
        )


def generate_response(prompt):
    completion = client.chat.completions.create(
        model="nvidia/nemotron-3-ultra-550b-a55b",
        messages=[
            {"role": "user", "content": str(prompt)}
        ],
        temperature=0.6,
        max_tokens=4000
    )

    return completion.choices[0].message.content
