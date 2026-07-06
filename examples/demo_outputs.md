# Demo Outputs

Below are the expected agent outputs for each demo input.

## 1. Output for: `I very like table tennis.`
- **Card Type**: `error_card`
- **Corrected Version**: `I like table tennis very much.` or `I really like table tennis.`
- **Grammar Error Type**: `Word Order / Adverb Placement`
- **Chinese Explanation**: 在英语中，表示非常喜欢某物时，通常不用 "very like"。可以用 "like ... very much" 或是 "really like"。"very" 不能直接修饰动词 "like"。
- **Natural Rewrite**: `I really like playing ping pong.`
- **Formal Rewrite**: `I possess a keen interest in table tennis.`
- **Suggested Tags**: `['verbs', 'adverbs', 'word-order']`
- **Memory Card Style Output (JSON)**:
  ```json
  {
    "card_type": "error_card",
    "corrected_version": "I really like table tennis.",
    "chinese_explanation": "在英语中，表示非常喜欢某物时，通常不用 'very like'。可以用 'like ... very much' 或是 'really like'。'very' 不能直接修饰动词 'like'。",
    "key_expression": null,
    "natural_version": "I really like playing ping pong.",
    "formal_version": "I possess a keen interest in table tennis.",
    "error_type": "Word Order / Adverb Placement",
    "scenario": "Hobbies & Leisure",
    "tags": ["verbs", "adverbs", "word-order"]
  }
  ```

---

## 2. Output for: `I am interesting in learning Swedish.`
- **Card Type**: `error_card`
- **Corrected Version**: `I am interested in learning Swedish.`
- **Grammar Error Type**: `Participle Adjectives (-ed vs -ing)`
- **Chinese Explanation**: "-ing" 结尾的形容词（如 interesting）常用于描述事物的特征（令人感兴趣的）；而 "-ed" 结尾的形容词（如 interested）则用于描述人的感受（感到感兴趣的）。在此处主语是 "I"（人），应使用 "interested in"。
- **Natural Rewrite**: `I'm keen on picking up Swedish.`
- **Formal Rewrite**: `I am interested in obtaining Swedish language skills.`
- **Suggested Tags**: `['adjectives', 'grammar', 'prepositions']`
- **Memory Card Style Output (JSON)**:
  ```json
  {
    "card_type": "error_card",
    "corrected_version": "I am interested in learning Swedish.",
    "chinese_explanation": "'-ing' 结尾的形容词常用于描述事物的特征（令人感兴趣的）；而 '-ed' 结尾的形容词则用于描述人的感受（感到感兴趣的）。主语是人时，应使用 'interested in'。",
    "key_expression": null,
    "natural_version": "I'm keen on picking up Swedish.",
    "formal_version": "I am interested in obtaining Swedish language skills.",
    "error_type": "Participle Adjectives (-ed vs -ing)",
    "scenario": "Language Learning",
    "tags": ["adjectives", "grammar", "prepositions"]
  }
  ```

---

## 3. Output for: `I enjoy the sense of accomplishment after exercising.`
- **Card Type**: `expression_card`
- **Corrected Version**: null
- **Chinese Explanation**: "sense of accomplishment" 是一个常用搭配，表示“成就感”。常用于表达通过努力完成某事后获得的满足和自豪。
- **Key Expression**: `sense of accomplishment`
- **Natural Rewrite**: `I love the feeling of achievement after a good workout.`
- **Formal Rewrite**: `I find physical exercise offers a notable sense of accomplishment upon completion.`
- **Suggested Tags**: `['vocabulary', 'nouns', 'collocation']`
- **Memory Card Style Output (JSON)**:
  ```json
  {
    "card_type": "expression_card",
    "corrected_version": null,
    "chinese_explanation": "'sense of accomplishment' 是一个常用搭配，表示'成就感'。常用于表达通过努力完成某事后获得的满足和自豪。",
    "key_expression": "sense of accomplishment",
    "natural_version": "I love the feeling of achievement after a good workout.",
    "formal_version": "I find physical exercise offers a notable sense of accomplishment upon completion.",
    "error_type": null,
    "scenario": "Health & Fitness",
    "tags": ["vocabulary", "nouns", "collocation"]
  }
  ```

---

## 4. Output for: `I was wondering if you could help me with this.`
- **Card Type**: `rewrite_card`
- **Corrected Version**: null
- **Chinese Explanation**: "I was wondering if you could..." 是一种非常委婉、礼貌地请求他人帮助的句型，使用过去进行时使语气听起来更加柔和客气。
- **Key Expression**: `I was wondering if you could`
- **Natural Rewrite**: `Could you give me a hand with this?`
- **Formal Rewrite**: `I am writing to inquire if you would be able to assist me with this task.`
- **Suggested Tags**: `['polite-phrases', 'request', 'verbs']`
- **Memory Card Style Output (JSON)**:
  ```json
  {
    "card_type": "rewrite_card",
    "corrected_version": null,
    "chinese_explanation": "'I was wondering if you could...' 是一种非常委婉、礼貌地请求他人帮助的句型，使用过去进行时使语气听起来更加柔和客气。",
    "key_expression": "I was wondering if you could",
    "natural_version": "Could you give me a hand with this?",
    "formal_version": "I am writing to inquire if you would be able to assist me with this task.",
    "error_type": null,
    "scenario": "Asking for Help",
    "tags": ["polite-phrases", "request", "verbs"]
  }
  ```

---

## 5. Output for Search Query: `成就感`
Expected search results return Example 3:
```
Found 1 saved cards.
--------------------------------------------------
[Expression Card] I enjoy the sense of accomplishment after exercising.
- Original Input: I enjoy the sense of accomplishment after exercising.
- Key Expression: sense of accomplishment
- Explanation (CN): 'sense of accomplishment' 是一个常用搭配，表示'成就感'。常用于表达通过努力完成某事后获得的满足和自豪。
- Natural: I love the feeling of achievement after a good workout.
- Formal: I find physical exercise offers a notable sense of accomplishment upon completion.
```

---

## 6. Output for Review Query: `review my recent cards`
Expected rule-based review quiz generation output format:
```json
{
  "total_questions": 1,
  "questions": [
    {
      "card_id": 3,
      "question_type": "translate_chinese",
      "question_text": "Recall or write down the English expression that matches this Chinese meaning:\n\"'sense of accomplishment' 是一个常用搭配，表示'成就感'。常用于表达通过努力完成某事后获得的满足和自豪。\"\nContext: \"I enjoy the sense of accomplishment after exercising.\"",
      "options": [],
      "correct_answer": "sense of accomplishment",
      "explanation": "Original sentence: I enjoy the sense of accomplishment after exercising."
    }
  ]
}
```
