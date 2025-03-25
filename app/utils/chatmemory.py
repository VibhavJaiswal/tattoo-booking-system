
import json
from difflib import SequenceMatcher

def load_qa_pairs(file_path="data/tattoo_chatbot_qa.json"):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def find_best_answer(question, qa_data, threshold=0.6):
    question_lower = question.lower()
    best_match = None
    highest_score = 0

    for pair in qa_data:
        stored_q = pair["question"].lower()
        score = SequenceMatcher(None, question_lower, stored_q).ratio()
        if score > highest_score:
            highest_score = score
            best_match = pair

    if best_match and highest_score >= threshold:
        return best_match["answer"]
    else:
        return "I'm not sure, but I can help you find the right tattoo information!"
