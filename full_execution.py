from model_loader import generate_response
from vector_db import db
from ragEngine import pipeline
import json


def full_execution(toon_file_path, question):

    with open(toon_file_path, "r", encoding="utf-8") as file:
        transcript = file.read()

    response = generate_response(f"""

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
* university
* topic/category
* course (if mentioned, otherwise empty string)

topic MUST be one of:

fees or courses
hostel
placement
eligibility
scholarship
refund
admission
course
infrastructure
facilities
ranking
accreditation

Conversation Transcript:

{transcript}

Return STRICT JSON ONLY.

{{
    "claims": [
        {{
            "claim": "",
            "topic": "",
            "university": "",
            "course": ""
        }}
    ]
}}

""")

    print("Raw Claims Response:")
    print(response)

    response = response.strip()

    if response.startswith("```json"):
        response = response.replace("```json", "", 1)

    if response.startswith("```"):
        response = response.replace("```", "", 1)

    if response.endswith("```"):
        response = response[:-3]

    response = response.strip()

    try:
        claims_json = json.loads(response)

        retrieved_chunks = []

        for claim in claims_json.get("claims"):

            filter_dict = {
            "$and": [
            {"university": claim["university"]},
            {"category": claim["topic"]},
            {"course": claim["course"]}
            ]}

            docs = db.similarity_search(
            query=claim["claim"],
            k=5,
            filter=filter_dict
            )
            retrieved_chunks.extend(docs)

        print(f"Retrieved Chunks: {len(docs)},{docs}")
    


    except Exception as e:
        print("Claims extraction failed:", e)
        print("Raw response:", repr(response))

        claims_json = {"claims": []}
        retrieved_chunks = []

    final_response = pipeline(
        question,
        transcript,
        retrieved_chunks,
        claims_json
    )

    print(final_response)

    return final_response