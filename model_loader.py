from dotenv import load_dotenv
import whisperx
import os
from openai import OpenAI
load_dotenv()


# api=os.getenv("GEMINI_API_KEY")
WHISPER_MODEL=os.getenv("WHISPER_MODEL")
WHISPER_DEVICE=os.getenv("WHISPER_DEVICE")
HF_TOKEN=os.getenv("HF_TOKEN")


def load_models():
    global client,model
    client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = os.getenv('NEMOTRON')
)

    model = whisperx.load_model(
        WHISPER_MODEL,
        device=WHISPER_DEVICE,
        compute_type="int8"
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