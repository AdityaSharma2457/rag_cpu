from historydb import add_to_history_db, search_historydb
from vector_db import broucher_db
from history_manager import save_conversation
from ragEngine import chat_pipeline_llm
from history_manager import get_recent_history


def chat_pipeline(question):
    chat_history = get_recent_history()
    history_results = search_historydb(question, k=3)
    broucher_results = broucher_db.similarity_search_with_score(question, k=3)

    history_score = history_results[0][1] if history_results else float("inf")
    broucher_score = broucher_results[0][1] if history_results else float("inf")

    if history_score < broucher_score:
        selected_results = history_results
    else:
        selected_results = broucher_results

    if selected_results:
        print(selected_results[0])
    
    response = chat_pipeline_llm(question, selected_results, chat_history)
    save_conversation(question, response)
    add_to_history_db(question, response)

    return {
        "success": True,
        "answer": response
    }