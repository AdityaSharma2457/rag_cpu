from model_loader import generate_response
from transcription import toon_file_path
from chromadb import retriever
from ragEngine import pipeline
from transcription import question

def full_execution():
    with open(toon_file_path, "r", encoding="utf-8") as file:
            transcript = file.read()



    claims_json=generate_response(f"""


    You are an expert university counselling auditor.

    Analyze the provided counselling conversation transcript.

    Your job is to identify ONLY factual claims made by the counsellor that can be verified using university brochures or official university documents.

    Extract claims related to:

    * Course Fees
    * Hostel Fees
    * Scholarships
    * Eligibility Criteria
    * Placements
    * Packages
    * Admission Process
    * Course Duration
    * Infrastructure
    * Hostel Facilities
    * Refund Policies
    * Seat Availability
    * Ranking
    * Accreditation
    * Course Curriculum
    * University Facilities
    * Any other factual university-related information

    DO NOT extract:

    * Greetings
    * Sales language
    * Persuasion
    * Behavioural statements
    * Opinions
    * Emotional statements
    * Small talk

    For every claim return:

    * exact claim
    * topic/category

    Conversation Transcript:

    {transcript}

    Return STRICT JSON ONLY.

    {
    "claims": [
    {
    "claim": "",
    "topic": "",
    "university":"",
    }
    ]
    }

    """)


    retrieved_chunks=[retriever.invoke(f"{i.university} ,{i.topic},{i.claim}" ) for i in claims_json["claims"]]

    response=pipeline(question,transcript,retrieved_chunks,claims_json)
    
    print(response)