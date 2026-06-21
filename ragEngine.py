from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from flask import Blueprint
from transcription import question as user_question
from model_loader import generate_response
from chromadb import retriever
from langchain_core.runnables import RunnableLambda
rag_path_bp=Blueprint("rag_call",__name__)
@rag_path_bp("/engine")


def pipeline(user_question,transcription_path,retrieved_context,claims_json):
    prompt = ChatPromptTemplate.from_template(f"""
    You are an expert Conversation Intelligence and University Counselling Quality Analyst.

    You are provided with:

    1. Counselling Conversation Transcript
    2. Extracted Counsellor Claims
    3. Official University Context retrieved from brochures
    4. Optional User Question

    ---

    TASK 1: FACTUAL CORRECTNESS

    For every extracted claim:

    Compare it against the official university context.

    Classify each claim as:

    * Correct
    * Incorrect
    * Partially Correct
    * Insufficient Information

    Provide reasoning.

    ---

    TASK 2: PROFESSIONALISM ANALYSIS

    Evaluate:

    * Professionalism
    * Communication Skills
    * Behaviour & Courtesy
    * Lead Conversion Ability
    * Objection Handling
    * Product Knowledge
    * Confidence
    * Empathy
    * SOP Adherence
    * Overall Performance

    Score each metric from 0 to 10.

    For every score provide:

    * score
    * explanation
    * evidence from conversation

    ---

    TASK 3: USER QUESTION

    If a user question exists:

    Answer it using both:

    * conversation transcript
    * university context

    If no user question exists:

    Return null.

    ---

    SCORING GUIDELINES

    Professionalism:

    * Greeting quality
    * Respectfulness
    * Tone
    * Structured communication

    Communication:

    * Clarity
    * Fluency
    * Information delivery

    Lead Conversion:

    * Discovery questions
    * Follow-up attempts
    * Call-to-action
    * Handling hesitation

    Objection Handling:

    * Responding to concerns
    * Addressing fees concerns
    * Addressing eligibility concerns

    Product Knowledge:

    * Accuracy of university information
    * Depth of knowledge

    Empathy:

    * Understanding student concerns
    * Personalization

    SOP Adherence:

    * Following expected counselling process

    ---

    Conversation Transcript:

    {transcription_path}

    ---

    Extracted Claims:

    {claims_json}

    ---

    Retrieved University Context:

    {retrieved_context}

    ---

    Return STRICT JSON ONLY.

    {
    "correctness": {
    "score": 0,
    "summary": "",
    "claim_results": [
    {
    "claim": "",
    "status": "",
    "reason": ""
    }
    ]
    },

    "scores": {
    "professionalism": {
    "score": 0,
    "evidence": [],
    "explanation": ""
    },

    ```
    "communication": {
      "score": 0,
      "evidence": [],
      "explanation": ""
    },

    "behaviour": {
      "score": 0,
      "evidence": [],
      "explanation": ""
    },

    "lead_conversion": {
      "score": 0,
      "evidence": [],
      "explanation": ""
    },

    "objection_handling": {
      "score": 0,
      "evidence": [],
      "explanation": ""
    },

    "product_knowledge": {
      "score": 0,
      "evidence": [],
      "explanation": ""
    },

    "confidence": {
      "score": 0,
      "evidence": [],
      "explanation": ""
    },

    "empathy": {
      "score": 0,
      "evidence": [],
      "explanation": ""
    },

    "sop_adherence": {
      "score": 0,
      "evidence": [],
      "explanation": ""
    },

    "overall_performance": {
      "score": 0,
      "explanation": ""
    }
    ```

},

"question_answer": null
}

    """)

    llm = RunnableLambda(generate_response)
    chain = (
        {
            "question": RunnablePassthrough() # or lambda x:x (runnablepassthrough just passes the pormpt as it is)
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    response = chain.invoke(f"{user_question}")
    return response