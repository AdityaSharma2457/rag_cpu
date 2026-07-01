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


def start_followup_session(report: str) -> dict:
    """
    Initialize a follow-up chat session with the report.

    Args:
        report: The complete generated report

    Returns:
        A session dictionary containing the report and empty history
    """
    return {
        "report": report,
        "history": []
    }


def process_followup(session: dict, user_question: str) -> dict:
    """
    Process a follow-up question and update session history.

    Args:
        session: The chat session dictionary
        user_question: The user's question

    Returns:
        Updated session with the new Q&A added to history
    """
    answer = ask_followup_question(
        report=session["report"],
        user_question=user_question,
        history=session["history"]
    )

    session["history"].append({
        "question": user_question,
        "answer": answer
    })

    return session


# Example usage / CLI interface
if __name__ == "__main__":
    import sys

    # Example: Read report from a file or use a sample
    sample_report = """
# Conversation Intelligence Report

## Factual Correctness Analysis
- Claim 1: "Course fee is $50,000" → CORRECT (verified from university brochure)
- Claim 2: "100% placement guarantee" → INCORRECT (brochure states 85% placement rate)
- Claim 3: "Hostel fee includes meals" → PARTIALLY CORRECT (only basic hostel fee mentioned)

## Professionalism Analysis
- Professionalism: 8/10 - Good greeting, respectful tone
- Communication: 7/10 - Clear but occasionally used jargon
- Lead Conversion: 6/10 - Limited discovery questions
- Objection Handling: 7/10 - Addressed fee concerns well
- Product Knowledge: 5/10 - Some inaccuracies in claims
- Overall Performance: 7/10
"""

    print("🤖 Follow-up Chat Session Started")
    print("=" * 50)
    print("Ask questions about the report. Type 'exit' to quit.\n")

    session = start_followup_session(sample_report)

    while True:
        user_input = input("❓ Your question: ").strip()
        if user_input.lower() in ['exit', 'quit', 'q']:
            print("👋 Goodbye!")
            break

        if not user_input:
            continue

        session = process_followup(session, user_input)
        print(f"\n💡 Answer:\n{session['history'][-1]['answer']}\n")
        print("-" * 50)