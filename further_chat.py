"""
Follow-up Chat Module for Report Q&A

This module handles follow-up questions from users based on the generated
conversation intelligence report. It maintains conversation history and
uses the LLM to answer questions with the report as context.
"""

from model_loader import generate_response


def ask_followup_question(report: str, user_question: str, history: list = None) -> str:
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
    history_text = ""
    if history and len(history) > 0:
        history_text = "\n\nPrevious Follow-up Q&A:\n"
        for i, msg in enumerate(history[-5:], 1):  # Last 5 exchanges for context
            history_text += f"Q{i}: {msg.get('question', '')}\n"
            history_text += f"A{i}: {msg.get('answer', '')}\n\n"

    prompt = f"""You are an expert Conversation Intelligence Analyst helping a user understand a counselling quality report.

GENERATED REPORT (for reference):
---
{report}
---

{history_text}

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









