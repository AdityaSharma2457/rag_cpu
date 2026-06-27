from model_loader import generate_response
from vector_db import collection
from ragEngine import pipeline
import json



def full_execution(toon_file_path, question):

    with open(toon_file_path, "r", encoding="utf-8") as file:
        transcript = file.read()

    claims_json = generate_response(f"""

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
    claims_json = json.loads(claims_json)

    retrieved_chunks=[collection.similarity_search(f"{query}",k=5 ) for query in claims_json["claims"]] 

    response=pipeline(question,transcript,retrieved_chunks,claims_json) 

    print(response)
    return response