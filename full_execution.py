from model_loader import generate_response
from vector_db import collection
from ragEngine import pipeline
import json
import re
import os
from db import history_table,transcription_table
from db_init_ import db
import uuid

os.makedirs("./reports", exist_ok=True)


def full_execution(session_id,toon_file_path, question):

    with open(toon_file_path, "r", encoding="utf-8") as file:
        transcript = file.read()

    # Generate claims from transcript using LLM
    llm_response = generate_response(f"""
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

The vector database contains university brochure information, where each chunk is written as a natural-language sentence.

Chunk structure:
- Every chunk starts with the university name.
- This is followed by the relevant information such as course, fees, hostel, scholarship, eligibility, placements, etc.
- University names and course aliases may also be present in the chunk.

Your task is to generate optimized semantic search queries for retrieving the correct chunks from the vector database.

Guidelines:
1. Generate one search query for every factual claim extracted from the conversation.
2. Every query MUST contain the university name.
3. Include the course name whenever it is available in the claim.
4. Include the appropriate category keyword depending on the claim:
   - "fees" for fee-related claims
   - "hostel" for hostel-related claims
   - "scholarship" for scholarship-related claims
   - "eligibility" for eligibility-related claims
   - "placement" for placement-related claims
   - Similarly include other relevant category keywords whenever applicable.
5. The query should be written as a natural-language sentence rather than a list of keywords.
6. Include all important information from the claim so that semantic similarity search retrieves the most relevant chunk.
7. If the course name is not explicitly mentioned, infer the most appropriate query using the available context without inventing facts.
8. Do not generate duplicate or unnecessary queries.

Return ONLY valid JSON in the following format:

{{
  "claims": [
    "query 1",
    "query 2",
    "query 3"
  ]
}}
""")

    # Extract JSON from LLM response (handle cases where LLM adds extra text)
    try:
        # Try to parse directly first
        claims_json = json.loads(llm_response)
    except json.JSONDecodeError:
        # Try to extract JSON from the response using regex
        json_match = re.search(r'\{.*\}', llm_response, re.DOTALL)
        if json_match:
            try:
                claims_json = json.loads(json_match.group())
            except json.JSONDecodeError:
                # Fallback: return empty claims
                print(f"Warning: Could not parse claims JSON from LLM response: {llm_response}")
                claims_json = {"claims": []}
        else:
            print(f"Warning: No JSON found in LLM response: {llm_response}")
            claims_json = {"claims": []}

    print("Claims JSON:", claims_json)

    retrieved_chunks = [collection.similarity_search(f"{query}", k=5) for query in claims_json["claims"]]

    response = pipeline(question, transcript, retrieved_chunks, claims_json)
    if (response):
        report_name = str(uuid.uuid4())
        with open(f"./reports/{report_name}.txt", "w", encoding="utf-8") as f:
            f.write(response)

        report_file_path = os.path.join(os.getcwd(), "reports", f"{report_name}.txt")

        transcript = db.session.get(transcription_table, session_id)
        if  transcript is None:
            return {
    "success": False,
    "answer": "transcript not found",

    }
        transcript.report_path_in_webserver=report_file_path
        transcript.status = "completed"

        db.session.commit()

        history = history_table()

        db.session.add(history)
        history.session_id=session_id
        history.history = json.dumps({"history":[{"question":question,"report":response}]})
        db.session.commit()    
    return {
    "success": True,
    "answer": response,

    }