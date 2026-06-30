from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from model_loader import generate_response
from langchain_core.runnables import RunnableLambda


def pipeline(user_question,transcript,retrieved_context,claims_json):
    user_question = user_question if user_question else "None"
    prompt = ChatPromptTemplate.from_template("""
    You are an expert Conversation Intelligence and University Counselling Quality Analyst.

    You are provided with:

    1. Counselling Conversation Transcript
    2. Extracted Counsellor Claims
    3. Official University Context retrieved from brochures
    4. Optional User Request

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
    question :
    {user_question}

    Conversation Transcript:

    {transcript}

    ---

    Extracted Claims:

    {claims_json}

    ---

    Retrieved University Context:

    {retrieved_context}
    """)

    llm = RunnableLambda(generate_response)
    chain = (
    prompt
    | llm
    | StrOutputParser()
)
    payload = {
        "user_question": user_question,
        "transcript": transcript,
        "claims_json": str(claims_json),
        "retrieved_context": str(retrieved_context)
    }
    
    print(payload)
    
    response = chain.invoke(payload)
    return response




def chat_pipeline_llm(question, retrieved_context, chat_history=None):

    prompt = ChatPromptTemplate.from_template("""
    You are an AI assistant for a university counselling CRM.

    You have access to:

    1. Recent Chat History
    2. Retrieved Context
    3. Current User Question

    Instructions:

    - Use the recent chat history to maintain conversational continuity.
    - Use the retrieved context as the factual source.
    - If the retrieved context contradicts the history, prefer the retrieved context.
    - Do not invent information.
    - If the answer cannot be found, say you don't have enough information.

    Recent Chat History:
    {chat_history}

    Retrieved Context:
    {retrieved_context}

    Current User Question:
    {question}
    """)

    llm = RunnableLambda(generate_response)

    chain = (
        prompt
        | llm
        | StrOutputParser()
    )

    payload = {
        "question": question,
        "retrieved_context": str(retrieved_context),
        "chat_history" : chat_history
    }

    response = chain.invoke(payload)
    return response