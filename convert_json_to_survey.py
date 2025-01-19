import requests
import json




# 1. SurveyMonkey OAuth2 access token
SURVEYMONKEY_ACCESS_TOKEN = "lMsBrzQ04CQ89elrGwz-g09hdNqcr3MAIEWmrV0xhPW7.ig4OVewpHmN7Fwmigs5pq1q.Y8tSkcyCfv4xY8PrzL0LqLPwjtlPO6l7iF9LC7Ghtpl3cVH-KZ2o7-5N0lY"

# 2. Headers for making authenticated requests
HEADERS = {
    "Authorization": f"Bearer {SURVEYMONKEY_ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def create_survey(title="Conversation Survey"):
    """
    Create a new survey. Returns survey_id.
    """
    url = "https://api.surveymonkey.com/v3/surveys"
    payload = {"title": title}
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()["id"]

def get_default_page_id(survey_id):
    """
    Returns the ID of the first (default) page that SurveyMonkey
    automatically creates for a new survey.
    """
    url = f"https://api.surveymonkey.com/v3/surveys/{survey_id}/pages"
    resp = requests.get(url, headers=HEADERS)
    resp.raise_for_status()
    pages_data = resp.json()
    if pages_data["data"]:
        return pages_data["data"][0]["id"]
    return None

def create_page(survey_id, title="Feedback Questions"):
    """
    Optionally create an additional page (if needed).
    Returns page_id.
    """
    url = f"https://api.surveymonkey.com/v3/surveys/{survey_id}/pages"
    payload = {"title": title}
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()["id"]

def create_question(survey_id, page_id, question_text):
    """
    Create a single-choice question with answers: Positive / Neutral / Negative.
    Returns the full JSON response which includes question_id, etc.
    """
    url = f"https://api.surveymonkey.com/v3/surveys/{survey_id}/pages/{page_id}/questions"
    payload = {
        "headings": [{"heading": question_text}],
        "family": "single_choice",
        "subtype": "vertical",
        "answers": {
            "choices": [
                {"text": "Positive"},
                {"text": "Neutral"},
                {"text": "Negative"}
            ]
        }
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()

def create_collector_for_survey(survey_id, name="ImportCollector"):
    """
    Create a collector for the given survey.
    This is required to use POST /collectors/{collector_id}/responses.
    Returns collector_id.
    """
    url = f"https://api.surveymonkey.com/v3/surveys/{survey_id}/collectors"
    payload = {"name": name,
               "type": "weblink"}
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()["id"]

def submit_response_to_collector(collector_id, page_id, question_answers):
    """
    Submit a single completed response to the collector via
    POST /collectors/{collector_id}/responses.

    :param collector_id: The collector's ID
    :param page_id: The survey page ID containing the questions
    :param question_answers: list of dicts, each with:
                            {
                              "id": question_id,
                              "answers": [ {"choice_id": some_choice_id} ]
                            }
    You can set response_status to "completed" or "in_progress" depending on your account.
    """
    url = f"https://api.surveymonkey.com/v3/collectors/{collector_id}/responses"
    payload = {
        "pages": [
            {
                "id": page_id,
                "questions": question_answers
            }
        ],
        "response_status": "completed"  # or "in_progress", etc., if allowed
    }
    resp = requests.post(url, headers=HEADERS, json=payload)
    resp.raise_for_status()
    return resp.json()

def main():
    # 1. Load JSON from conversation_summary.json
    with open("conversation_summary.json", "r", encoding="utf-8") as f:
        summary_data = json.load(f)
        # Example:
        # [
        #   {
        #     "question": "...",
        #     "sentiment": "positive/neutral/negative",
        #     "topic": "...",
        #     "followUpQuestion": null or ...
        #   },
        #   ...
        # ]

    # 2. Create a new survey
    survey_id = create_survey("New Feedback from Conversation")
    print(f"Created Survey ID: {survey_id}")

    # 3. Get the default page (created automatically by SurveyMonkey)
    page_id = get_default_page_id(survey_id)
    if not page_id:
        # If there's no default page for some reason, create one:
        page_id = create_page(survey_id, title="Feedback Page")
    print(f"Using Page ID: {page_id}")

    # 4. Create questions & track question IDs + choice IDs
    # We'll build "question_answers" after we know which choice matches sentiment
    question_answers_for_submit = []  # for the eventual POST to the collector
    for item in summary_data:
        q_text = item.get("question", "Untitled question")
        sentiment = item.get("sentiment", "").lower()  # e.g., "positive"

        print(f"Creating question: {q_text}")
        created_question_data = create_question(survey_id, page_id, q_text)
        question_id = created_question_data["id"]

        # "choices" typically in created_question_data["answers"]["choices"]
        choice_list = created_question_data.get("answers", {}).get("choices", [])
        chosen_choice_id = None
        for c in choice_list:
            # If sentiment == "positive" and c["text"] == "Positive", match
            if sentiment and sentiment in c["text"].lower():
                chosen_choice_id = c["id"]
                break

        if chosen_choice_id:
            # We store in the format required by "submit_response_to_collector"
            # i.e. each "question" has "id": question_id, "answers": [...]
            question_answers_for_submit.append({
                "id": question_id,
                "answers": [{"choice_id": chosen_choice_id}]
            })
        else:
            # No matching sentiment => we won't preselect an answer
            print(f"Warning: No matching sentiment for question '{q_text}'")

    # 5. Create a collector for the survey
    collector_id = create_collector_for_survey(survey_id, name="ImportCollector")
    print(f"Created Collector ID: {collector_id}")

    # 6. Submit a single response to the collector (if we have any chosen answers)
    if question_answers_for_submit:
        print("Submitting a response using the sentiment-based answers...")
        created_response = submit_response_to_collector(
            collector_id,
            page_id,
            question_answers_for_submit
        )
        print("Response submission success:", created_response)
    else:
        print("No valid answers to submit (no sentiments matched).")

    print(f"View/Edit Survey: https://www.surveymonkey.com/create/?sm={survey_id}")

if __name__ == "__main__":
    main()
