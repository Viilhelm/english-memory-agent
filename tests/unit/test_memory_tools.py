import os
import pytest
import sqlite3
from english_memory_agent.database import db
from english_memory_agent.tools import memory_tools, review_tools


TEST_DB_PATH = os.path.join(os.path.dirname(__file__), "test_memory.db")

@pytest.fixture(autouse=True)
def setup_test_db():
    # Override database path in db module
    original_db_path = db.DB_PATH
    db.DB_PATH = TEST_DB_PATH
    
    # Initialize the database
    db.init_db()
    
    yield
    
    # Clean up the test database file
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except PermissionError:
            pass
    db.DB_PATH = original_db_path

def test_init_db():
    # Ensure database file exists and contains the cards table
    assert os.path.exists(TEST_DB_PATH)
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cards'")
    row = cursor.fetchone()
    conn.close()
    assert row is not None

def test_save_card_success():
    card_data = {
        "card_type": "error_card",
        "original_input": "She do not like apples.",
        "corrected_version": "She does not like apples.",
        "natural_version": "She doesn't like apples.",
        "formal_version": "She does not prefer apples.",
        "chinese_explanation": "第三人称单数助动词用does而不是do",
        "key_expression": "does not like",
        "error_type": "Subject-Verb Agreement",
        "scenario": "Daily life",
        "tags": "grammar,verbs"
    }
    
    res = memory_tools.save_card(card_data)
    assert res["status"] == "success"
    assert res["card_id"] is not None
    assert res["safe_to_save"] is True
    
    # Verify card exists in database
    conn = sqlite3.connect(TEST_DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cards WHERE id = ?", (res["card_id"],))
    row = cursor.fetchone()
    conn.close()
    
    assert row is not None
    assert row[1] == "error_card"
    assert row[2] == "She do not like apples."
    assert row[3] == "She does not like apples."
    assert row[7] == "第三人称单数助动词用does而不是do"
    assert row[11] == "grammar,verbs"

def test_save_card_privacy_blocked():
    card_data = {
        "card_type": "expression_card",
        "original_input": "My email is secret@google.com, send me there.",
        "chinese_explanation": "含有隐私信息，不予保存"
    }
    
    res = memory_tools.save_card(card_data)
    assert res["status"] == "error"
    assert res["card_id"] is None
    assert res["safe_to_save"] is False
    assert len(res["risks"]) > 0
    assert any("email" in risk for risk in res["risks"])

def test_search_cards():
    card1 = {
        "card_type": "expression_card",
        "original_input": "To bite the bullet means to face a difficult situation.",
        "chinese_explanation": "咬紧牙关，硬着头皮",
        "key_expression": "bite the bullet",
        "tags": "idioms,casual"
    }
    card2 = {
        "card_type": "error_card",
        "original_input": "I am looking forward to meet you.",
        "corrected_version": "I am looking forward to meeting you.",
        "chinese_explanation": "look forward to 后面加动名词",
        "key_expression": "look forward to meeting",
        "tags": "preposition,grammar"
    }
    
    memory_tools.save_card(card1)
    memory_tools.save_card(card2)
    
    # Search by key expression
    results = memory_tools.search_cards("bullet")
    assert len(results) == 1
    assert results[0]["key_expression"] == "bite the bullet"
    
    # Search by tag
    results = memory_tools.search_cards("grammar")
    assert len(results) == 1
    assert results[0]["corrected_version"] == "I am looking forward to meeting you."
    
    # Search by non-existent query
    results = memory_tools.search_cards("nonexistent")
    assert len(results) == 0

def test_list_recent_cards():
    for i in range(7):
        memory_tools.save_card({
            "card_type": "expression_card",
            "original_input": f"Sentence number {i}",
            "tags": f"tag{i}"
        })
        
    recent = memory_tools.list_recent_cards(limit=5)
    assert len(recent) == 5
    # The first in list should be the most recently added (ID 7)
    assert recent[0]["original_input"] == "Sentence number 6"
    assert recent[4]["original_input"] == "Sentence number 2"

def test_delete_card():
    res = memory_tools.save_card({
        "card_type": "expression_card",
        "original_input": "ToDelete",
        "tags": "temp"
    })
    card_id = res["card_id"]
    
    # Delete the card
    del_res = memory_tools.delete_card(card_id)
    assert del_res["status"] == "success"
    
    # Verify it is deleted
    results = memory_tools.search_cards("ToDelete")
    assert len(results) == 0
    
    # Try deleting again
    del_res_again = memory_tools.delete_card(card_id)
    assert del_res_again["status"] == "error"

def test_generate_quiz():
    cards = [
        {
            "id": 1,
            "card_type": "error_card",
            "original_input": "He go to school.",
            "corrected_version": "He goes to school.",
            "natural_version": "He is going to school.",
            "formal_version": "He is in attendance at school.",
            "chinese_explanation": "动词变单三",
            "error_type": "Tense"
        },
        {
            "id": 2,
            "card_type": "expression_card",
            "original_input": "Bite the bullet and finish.",
            "chinese_explanation": "硬着头皮",
            "key_expression": "bite the bullet",
            "natural_version": "Just do it.",
            "formal_version": "Proceed despite constraints."
        }
    ]
    
    quiz = review_tools.generate_review_quiz_from_cards(cards)
    assert quiz["total_questions"] == 2
    assert len(quiz["questions"]) == 2
    
    for q in quiz["questions"]:
        assert "question_type" in q
        assert "question_text" in q
        assert "correct_answer" in q
        assert "explanation" in q
        if q["question_type"] == "choose_rewrite":
            assert len(q["options"]) >= 2
