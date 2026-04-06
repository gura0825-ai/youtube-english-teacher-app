REQUIRED_ITEM_FIELDS = {"id", "question", "options", "answer"}
REQUIRED_OPTIONS = {"A", "B", "C", "D"}
VALID_ANSWERS = {"A", "B", "C", "D"}
EXPECTED_COUNT = 20


def validate_quiz(quiz_data: list) -> tuple[bool, str]:
    """
    Returns (is_valid, error_message).
    Validates quiz structure: count, required fields, options, answer values.
    """
    if not isinstance(quiz_data, list):
        return False, "Quiz data is not a list"

    if len(quiz_data) != EXPECTED_COUNT:
        return False, f"Expected {EXPECTED_COUNT} questions, got {len(quiz_data)}"

    for i, item in enumerate(quiz_data, start=1):
        if not isinstance(item, dict):
            return False, f"Question {i} is not a dict"

        missing_fields = REQUIRED_ITEM_FIELDS - set(item.keys())
        if missing_fields:
            return False, f"Question {i} missing fields: {missing_fields}"

        if not isinstance(item["options"], dict):
            return False, f"Question {i} options is not a dict"

        missing_opts = REQUIRED_OPTIONS - set(item["options"].keys())
        if missing_opts:
            return False, f"Question {i} missing option keys: {missing_opts}"

        if item["answer"] not in VALID_ANSWERS:
            return False, f"Question {i} has invalid answer: '{item['answer']}'"

    return True, ""
