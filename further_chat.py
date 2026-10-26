"""
Follow-up Chat Module for Report Q&A

This module handles follow-up questions from users based on the generated
conversation intelligence report. It maintains conversation history and
uses the LLM to answer questions with the report as context.
"""

from model_loader import generate_response
from db import get_history, get_transcription


def ask_followup_question( user_question: str, session_id: str) -> str:
    """
    Answer a follow-up question based on the generated report.

    Args:
        report: The complete generated report (factual correctness + professionalism analysis)
        user_question: The user's follow-up question
        history: Optional list of previous Q&A pairs for context

    Returns:
        The LLM's response to the follow-up question
    """
    # Format conversation history
    history = get_history(session_id)
    if history is None:
        raise ValueError("History not found")

    history_data = history["history"]

    if not history_data or "history" not in history_data:
        raise ValueError("History is empty")

    history_to_be_sent=history_data["history"][-5:]
    if (len(history_data["history"])>5):
        transcript = get_transcription(session_id)
        if transcript is None or not transcript["report_path_in_webserver"]:
            raise ValueError("Transcript report not found")
        with open(transcript["report_path_in_webserver"], "r", encoding="utf-8") as f:
            report = f.read()
    else:
        report="report is provided in the history chat"





    prompt = f"""You are an expert Conversation Intelligence Analyst helping a user understand a counselling quality report.

GENERATED REPORT (for reference):
---
{report}
---

{history_to_be_sent}

USER'S FOLLOW-UP QUESTION:
{user_question}

---

INSTRUCTIONS:
- Answer the user's question based ONLY on the information in the generated report above
- If the question asks about something NOT in the report, clearly state that the information is not available in the report
- Be specific and reference relevant sections of the report (e.g., "According to the Professionalism Analysis section...", "The Factual Correctness review shows...")
- Use markdown formatting for readability
- Include relevant emojis to make the response engaging
- Keep responses concise but comprehensive
- Do NOT make up information or hallucinate facts not present in the report"""

    response = generate_response(prompt)
    return response







