from english_memory_agent.database import db
from english_memory_agent.tools.privacy_tools import privacy_scan

def init_db() -> None:
    """Initializes the database schema."""
    db.init_db()

def save_card_to_db(
    card_type: str,
    original_input: str,
    corrected_version: str = None,
    natural_version: str = None,
    formal_version: str = None,
    chinese_explanation: str = None,
    key_expression: str = None,
    error_type: str = None,
    scenario: str = None,
    tags: str = None,
    part_of_speech: str = None,
    definition: str = None,
) -> dict:
    """
    Saves an English memory card to the SQLite database after running a privacy check.
    This is used by the MCP server and ADK function-calling.
    """
    scan_res = privacy_scan(original_input)
    
    if not scan_res["safe_to_save"]:
        return {
            "status": "error",
            "message": f"Security/Privacy Check Failed: {', '.join(scan_res['risks'])}",
            "card_id": None,
            "safe_to_save": False,
            "risks": scan_res["risks"]
        }
        
    card = {
        "card_type": card_type,
        "original_input": original_input,
        "corrected_version": corrected_version,
        "natural_version": natural_version,
        "formal_version": formal_version,
        "chinese_explanation": chinese_explanation,
        "key_expression": key_expression,
        "error_type": error_type,
        "scenario": scenario,
        "tags": tags,
        "part_of_speech": part_of_speech,
        "definition": definition,
    }
    try:
        card_id = db.insert_card(card)
        return {
            "status": "success",
            "message": f"Successfully saved card to database.",
            "card_id": card_id,
            "safe_to_save": True,
            "risks": []
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Database save failed: {str(e)}",
            "card_id": None,
            "safe_to_save": True,
            "risks": []
        }

def save_card(card: dict) -> dict:
    """Wrapper/forwarder to save_card_to_db."""
    return save_card_to_db(
        card_type=card.get("card_type", "expression_card"),
        original_input=card.get("original_input", ""),
        corrected_version=card.get("corrected_version"),
        natural_version=card.get("natural_version"),
        formal_version=card.get("formal_version"),
        chinese_explanation=card.get("chinese_explanation"),
        key_expression=card.get("key_expression"),
        error_type=card.get("error_type"),
        scenario=card.get("scenario"),
        tags=card.get("tags"),
        part_of_speech=card.get("part_of_speech"),
        definition=card.get("definition"),
    )

def search_cards(query: str) -> list[dict]:
    """
    Searches the saved cards using a search string.
    
    Args:
        query (str): The search query.
        
    Returns:
        list[dict]: A list of card dictionaries matching the query.
    """
    return db.query_cards(query)

def list_recent_cards(limit: int = 5) -> list[dict]:
    """
    Lists the most recently created cards.
    
    Args:
        limit (int): Maximum number of cards to return.
        
    Returns:
        list[dict]: A list of card dictionaries.
    """
    return db.fetch_recent_cards(limit)

def delete_card(card_id: int) -> dict:
    """
    Deletes a card by its database ID.
    
    Args:
        card_id (int): The ID of the card to delete.
        
    Returns:
        dict: A status dictionary containing 'status' and 'message'.
    """
    success = db.delete_card_by_id(card_id)
    if success:
        return {
            "status": "success",
            "message": f"Successfully deleted card ID {card_id}."
        }
    else:
        return {
            "status": "error",
            "message": f"Card ID {card_id} not found."
        }
