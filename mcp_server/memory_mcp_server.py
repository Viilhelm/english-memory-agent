import os
import json
from mcp.server.fastmcp import FastMCP

# Ensure the database path can be resolved correctly
# Load environment if running standalone
from dotenv import load_dotenv
load_dotenv()

# Import the existing English Memory Agent tools
from english_memory_agent.tools.memory_tools import (
    save_card_to_db,
    search_cards,
    list_recent_cards,
    delete_card
)
from english_memory_agent.tools.review_tools import generate_review_quiz_from_cards

# Create the FastMCP server
mcp = FastMCP("English Memory Agent Database Server")

@mcp.tool()
def save_memory_card(
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
) -> str:
    """
    Saves an English vocabulary or error card into the local SQLite memory database.

    Args:
        card_type: Must be 'error_card', 'rewrite_card', 'expression_card', or 'word_card'.
        original_text: The original raw sentence input.
        corrected_version: Grammatically corrected sentence (for error cards).
        natural_version: Conversational daily rewrite (sentence) or natural example sentence (word/phrase).
        formal_version: Formal workplace rewrite (sentence) or formal example sentence (word/phrase).
        chinese_explanation: Detailed Chinese explanation and usage notes.
        key_expression: Highlighted expression or phrase to learn.
        error_type: Classification of the grammatical error (e.g. Tense, Prepositions).
        scenario: Likely conversation context (e.g. Daily conversation, Workplace).
        tags: Categorization tags separated by commas.
        part_of_speech: Part of speech for word_card (e.g. 'noun', 'abbreviation').
        definition: Short English definition for word_card.
    """
    res = save_card_to_db(
        card_type=card_type,
        original_input=original_input,
        corrected_version=corrected_version,
        natural_version=natural_version,
        formal_version=formal_version,
        chinese_explanation=chinese_explanation,
        key_expression=key_expression,
        error_type=error_type,
        scenario=scenario,
        tags=tags,
        part_of_speech=part_of_speech,
        definition=definition,
    )
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def search_memory_cards(query: str) -> str:
    """
    Searches the memory database for saved cards matching the keyword.
    Looks across original sentences, corrections, Chinese explanations, key expressions, scenarios, and tags.
    
    Args:
        query: The search keyword (in English or Chinese).
    """
    cards = search_cards(query)
    if not cards:
        return f"No cards found matching query: '{query}'"
    return json.dumps(cards, indent=2, ensure_ascii=False)

@mcp.tool()
def list_recent_memory_cards(limit: int = 5) -> str:
    """
    Lists the most recently saved memory cards in the database.
    
    Args:
        limit: Max number of cards to retrieve (default is 5).
    """
    cards = list_recent_cards(limit)
    if not cards:
        return "No cards found in the database."
    return json.dumps(cards, indent=2, ensure_ascii=False)

@mcp.tool()
def delete_memory_card(card_id: int) -> str:
    """
    Deletes a memory card from the local SQLite database by its ID.
    
    Args:
        card_id: The integer ID of the card to delete.
    """
    res = delete_card(card_id)
    return json.dumps(res, indent=2, ensure_ascii=False)

@mcp.tool()
def generate_review_quiz(limit: int = 3) -> str:
    """
    Generates a list of review quiz questions based on the most recently saved cards.
    
    Args:
        limit: Number of questions to return (default is 3).
    """
    recent_cards = list_recent_cards(limit=50)
    if not recent_cards:
        return "No cards in the database to generate a quiz. Add some cards first!"
    
    quiz_data = generate_review_quiz_from_cards(recent_cards)
    questions = quiz_data.get("questions", [])[:limit]
    
    formatted_quiz = {
        "total_questions": len(questions),
        "questions": questions
    }
    return json.dumps(formatted_quiz, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    from english_memory_agent.tools.memory_tools import init_db
    init_db()
    mcp.run()
