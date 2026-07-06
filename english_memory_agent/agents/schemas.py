from pydantic import BaseModel, Field
from typing import List, Optional

class EnglishAnalysisResult(BaseModel):
    card_type: str = Field(
        description=(
            "Must be one of: "
            "'error_card' (input is a full sentence with grammar/spelling errors), "
            "'rewrite_card' (input is a full sentence that is correct but can be improved in style/tone/naturalness), "
            "'expression_card' (input is a phrase, collocation, idiom, or multi-word expression to learn), "
            "or 'word_card' (input is a single word, an abbreviation, or a technical term to learn)."
        )
    )
    corrected_version: Optional[str] = Field(
        None,
        description="The corrected version of the English sentence. Required if card_type is 'error_card'. Otherwise, leave null."
    )
    chinese_explanation: Optional[str] = Field(
        None,
        description=(
            "If 'error_card', explain the grammar errors in Chinese. "
            "If 'expression_card' or 'rewrite_card', explain the meaning, usage, and examples of the key expression in Chinese. "
            "If 'word_card', explain the word's meaning, part of speech, common collocations, and usage in Chinese."
        )
    )
    key_expression: Optional[str] = Field(
        None,
        description=(
            "The headword being learned. "
            "Required if card_type is 'expression_card' (the phrase/idiom/collocation) or 'word_card' (the word or abbreviation itself). "
            "Otherwise, leave null."
        )
    )
    natural_version: str = Field(
        description=(
            "For sentence inputs (error_card/rewrite_card): a natural, conversational English rewrite. "
            "For word/phrase inputs (word_card/expression_card): a natural, everyday example sentence using the headword."
        )
    )
    formal_version: str = Field(
        description=(
            "For sentence inputs: a formal, business or professional rewrite. "
            "For word/phrase inputs: a formal/professional example sentence using the headword."
        )
    )
    error_type: Optional[str] = Field(
        None,
        description="The grammar error type (e.g., 'Tense', 'Preposition', 'Subject-Verb Agreement', 'Spelling', 'Article') if card_type is 'error_card'. Otherwise, null."
    )
    part_of_speech: Optional[str] = Field(
        None,
        description="Part of speech of the headword (e.g., 'noun', 'verb', 'adjective', 'abbreviation', 'phrasal verb'). Required if card_type is 'word_card'. Otherwise, null."
    )
    definition: Optional[str] = Field(
        None,
        description="Short English definition of the headword. Required if card_type is 'word_card'. Otherwise, null."
    )
    scenario: str = Field(
        description="The likely scenario or context of this sentence (e.g., 'Daily Conversation', 'Business Email', 'Academic Paper', 'Travel')."
    )
    tags: List[str] = Field(
        default_factory=list,
        description="Categorization tags for grammar topics or vocabulary domains (e.g., ['verbs', 'tense', 'idiom', 'business'])."
    )

class RouterIntent(BaseModel):
    intent: str = Field(
        description="Classified user intent: 'analyze_new_english_input' (user enters text to analyze), 'search_memory' (user wants to search cards), 'generate_review' (user wants a review quiz), 'delete_card' (user wants to delete a card), or 'list_recent_cards' (user wants to list recent cards)."
    )
    search_query: Optional[str] = Field(
        None,
        description="The search query string extracted from user input if intent is 'search_memory'. Otherwise, null."
    )
    card_id: Optional[int] = Field(
        None,
        description="The card ID extracted from user input if intent is 'delete_card'. Otherwise, null."
    )
