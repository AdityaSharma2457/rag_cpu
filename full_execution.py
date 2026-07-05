from model_loader import generate_response
from vector_db import collection
from ragEngine import pipeline
import json
import re
import os
from db import history_table,transcription_table
from db_init_ import db
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

os.makedirs("./reports", exist_ok=True)


def batch_similarity_search(queries, k=5, max_workers=4, use_parallel=True):
    """
    Batch retrieve chunks for multiple queries with optimizations.
    
    Optimizations:
    1. Deduplicates identical queries
    2. Uses parallel ThreadPoolExecutor for concurrent searches
    3. Maps results back to original query order
    4. Adds timing and progress tracking
    """
    
    if not queries:
        return []
    
    start_time = time.time()
    
    # Step 1: Deduplicate queries
    print(f"📊 Processing {len(queries)} claims...")
    unique_queries = list(set(queries))
    print(f"   └─ {len(unique_queries)} unique queries after deduplication")
    
    # Step 2: Batch search with parallel execution
    retrieved_results = {}
    
    if use_parallel and len(unique_queries) > 1:
        print(f"⚡ Running {len(unique_queries)} parallel vector searches...")
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_query = {
                executor.submit(collection.similarity_search, q, k): q 
                for q in unique_queries
            }
            
            # Process results as they complete
            completed = 0
            for future in as_completed(future_to_query):
                completed += 1
                query = future_to_query[future]
                try:
                    chunks = future.result()
                    retrieved_results[query] = chunks
                    print(f"   └─ [{completed}/{len(unique_queries)}] Retrieved for: {query[:50]}...")
                except Exception as e:
                    print(f"   ⚠️  [{completed}/{len(unique_queries)}] Error retrieving for: {query[:50]}... - {str(e)}")
                    retrieved_results[query] = []  # Return empty list on error
    else:
        print(f"🔄 Running {len(unique_queries)} sequential vector searches...")
        
        for i, query in enumerate(unique_queries, 1):
            try:
                chunks = collection.similarity_search(query, k=k)
                retrieved_results[query] = chunks
                print(f"   └─ [{i}/{len(unique_queries)}] Retrieved for: {query[:50]}...")
            except Exception as e:
                print(f"   ⚠️  [{i}/{len(unique_queries)}] Error retrieving for: {query[:50]}... - {str(e)}")
                retrieved_results[query] = []
    
    # Step 3: Map results back to original query order (preserving duplicates)
    retrieved_chunks = [retrieved_results.get(q, []) for q in queries]
    
    elapsed = time.time() - start_time
    print(f"✅ Batch retrieval complete in {elapsed:.2f}s")
    print(f"   └─ Retrieved {sum(len(chunks) for chunks in retrieved_chunks)} total chunks")
    
    return retrieved_chunks


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

    claims = claims_json.get("claims", [])
    if not isinstance(claims, list):
        claims = []
    claims_json["claims"] = claims

    print("Claims JSON:", claims_json)

    # ✅ OPTIMIZED: Use batch retrieval instead of sequential
    retrieved_chunks = batch_similarity_search(claims, k=5, max_workers=4, use_parallel=True)

    response = pipeline(question, transcript, retrieved_chunks, claims_json)

    if (response):
        print("💾 Saving report...")
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
        
        transcript.report_path_in_webserver = report_file_path
        transcript.status = "completed"

        # Get or create history
        history = db.session.get(history_table, session_id)
        if history is None:
            history = history_table()
            history.session_id = session_id
            db.session.add(history)

        # Update history
        history.session_id = session_id
        history.history = {"history": [{"question": question, "report": response}]}
        
        # ✅ OPTIMIZED: Single commit instead of multiple
        db.session.commit()
        print("✅ Report saved successfully")
    
    return {
        "success": True,
        "answer": response,
    }
