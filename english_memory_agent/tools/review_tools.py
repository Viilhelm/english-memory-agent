import random

def generate_review_quiz_from_cards(cards: list[dict]) -> dict:
    """
    Generates an interactive review quiz from a list of cards.
    Supports four question types:
      - 'correct_sentence' (for error cards)
      - 'translate_chinese' (for expression cards)
      - 'explain_expression' (for expression cards)
      - 'choose_rewrite' (matching natural/formal rewrites)
      
    Args:
        cards (list[dict]): List of cards retrieved from the database.
        
    Returns:
        dict: A dictionary containing:
              - 'total_questions': int
              - 'questions': list[dict]
    """
    if not cards:
        return {"total_questions": 0, "questions": []}
        
    questions = []
    
    for idx, card in enumerate(cards):
        card_type = card.get("card_type", "expression_card")
        card_id = card.get("id")
        
        # Decide question type
        if card_type == "error_card":
            qtype = random.choice(["correct_sentence", "choose_rewrite"])
        else:
            qtype = random.choice(["translate_chinese", "explain_expression", "choose_rewrite"])
            
        q_item = {
            "card_id": card_id,
            "question_type": qtype,
            "question_text": "",
            "options": [],
            "correct_answer": "",
            "explanation": ""
        }
        
        if qtype == "correct_sentence":
            q_item["question_text"] = f"Correct the following English sentence:\n\"{card.get('original_input')}\""
            q_item["correct_answer"] = card.get('corrected_version', "")
            q_item["explanation"] = (
                f"Chinese Explanation:\n{card.get('chinese_explanation')}\n\n"
                f"Grammar Error Type: {card.get('error_type')}"
            )
            
        elif qtype == "translate_chinese":
            q_item["question_text"] = (
                f"Recall or write down the English expression that matches this Chinese meaning:\n"
                f"\"{card.get('chinese_explanation')}\"\n"
                f"Context: \"{card.get('original_input')}\""
            )
            q_item["correct_answer"] = card.get("key_expression", "")
            q_item["explanation"] = f"Original sentence: {card.get('original_input')}"
            
        elif qtype == "explain_expression":
            q_item["question_text"] = f"Explain the meaning and usage of the expression: \"{card.get('key_expression')}\""
            q_item["correct_answer"] = card.get("chinese_explanation", "")
            q_item["explanation"] = f"Context: \"{card.get('original_input')}\""
            
        elif qtype == "choose_rewrite":
            style = random.choice(["Natural", "Formal"])
            orig = card.get("original_input")
            natural = card.get("natural_version")
            formal = card.get("formal_version")

            q_item["question_text"] = f"Which of the following is the most {style.upper()} rewrite of the sentence: \"{orig}\"?"

            options_dict = {
                "Natural": natural,
                "Formal": formal
            }

            valid_options = {k: v for k, v in options_dict.items() if v}

            if len(valid_options) >= 2:
                shuffled_keys = list(valid_options.keys())
                random.shuffle(shuffled_keys)

                options_list = []
                correct_letter = "A"
                for idx_opt, key in enumerate(shuffled_keys):
                    letter = chr(65 + idx_opt)
                    options_list.append(f"{letter}: {valid_options[key]}")
                    if key == style:
                        correct_letter = letter

                q_item["options"] = options_list
                q_item["correct_answer"] = correct_letter
                q_item["explanation"] = (
                    f"Correct choice is {correct_letter} ({style} rewrite).\n\n"
                    f"Rewrites Reference:\n"
                    f"- Natural: {natural}\n"
                    f"- Formal: {formal}"
                )
            else:
                q_item["question_type"] = "correct_sentence"
                q_item["question_text"] = f"Correct the following English sentence:\n\"{card.get('original_input')}\""
                q_item["correct_answer"] = card.get("corrected_version", "") or card.get("original_input", "")
                q_item["explanation"] = f"Chinese Explanation:\n{card.get('chinese_explanation')}"
                
        questions.append(q_item)
        
    return {
        "total_questions": len(questions),
        "questions": questions
    }
