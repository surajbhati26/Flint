# assessment_engine.py
# ------------------------------------------------------------
# WHAT THIS FILE DOES:
# This is the "engine room" of our app. It's the only file that
# actually talks to the Gemini AI. Every other file just prepares
# data (like file_utils.py) or prepares instructions (ai_prompts.py).
# This file takes those instructions, sends them to the AI, and
# returns the AI's answer back to the app.
#
# WHY WE DO THIS:
# By putting ALL our AI calls in one file, if we ever need to switch
# AI providers (e.g., from Gemini to another service), we only need
# to update this ONE file instead of the whole app. This is a design
# principle called "separation of concerns."
# ------------------------------------------------------------

import google.generativeai as genai
import config
import ai_prompts


def configure_gemini():
    """
    WHAT: Sets up (authenticates) our connection to Google's Gemini AI
    using the API key from config.py.

    WHY: The AI service needs to know WHO is asking before it will
    respond. This function must run once before we make any AI calls.

    RETURNS: True if setup succeeded, False if something is wrong
    (like a missing API key), so the app can show a helpful error
    instead of crashing.
    """
    if not config.is_api_key_configured():
        return False

    try:
        genai.configure(api_key=config.GEMINI_API_KEY)
        return True
    except Exception:
        return False


def call_gemini(prompt_text):
    """
    WHAT: This is our single, reusable function for sending ANY prompt
    to the AI and getting back its text response.

    WHY: Instead of repeating the same "connect to AI and get a reply"
    code in 4 different places, we write it once here and reuse it.
    This is called "DRY" coding — Don't Repeat Yourself.

    HOW IT WORKS:
    1. We create a "model" object (like picking which AI brain to use).
    2. We send our prompt text to it.
    3. We return just the plain text part of its reply.
    """
    try:
        model = genai.GenerativeModel(config.MODEL_NAME)
        response = model.generate_content(prompt_text)
        return response.text
    except Exception as error:
        # If the AI call fails (bad internet, invalid key, quota limit, etc.)
        # we return a clear error message instead of letting the app crash.
        return f"ERROR: AI request failed. Details: {error}"


def extract_topics_from_document(document_text):
    """
    WHAT: High-level function used by app.py to get a summary + topic
    list from an uploaded document.

    WHY: app.py shouldn't need to know HOW prompts are built or HOW the
    AI is called — it just wants "give me the topics for this text."
    This function hides all that complexity (this is called an
    "abstraction layer").
    """
    prompt = ai_prompts.build_topic_extraction_prompt(document_text)
    ai_response = call_gemini(prompt)
    return ai_response


def generate_assessment_paper(topics_text, difficulty):
    """
    WHAT: High-level function to generate a full assessment paper
    (MCQ + short answer + essay questions) based on topics and
    a chosen difficulty.

    WHY: Same idea as above — app.py just calls this ONE function
    and gets back a ready-to-display question paper.
    """
    prompt = ai_prompts.build_question_generation_prompt(topics_text, difficulty)
    ai_response = call_gemini(prompt)
    return ai_response


def evaluate_student_answer(question_text, student_answer):
    """
    WHAT: High-level function to grade one student's answer and
    return a score + structured feedback.
    """
    prompt = ai_prompts.build_evaluation_prompt(question_text, student_answer)
    ai_response = call_gemini(prompt)
    return ai_response


def aggregate_class_feedback(all_evaluations_text):
    """
    WHAT: High-level function to summarize many evaluations into
    one class-wide feedback report.
    """
    prompt = ai_prompts.build_feedback_aggregation_prompt(all_evaluations_text)
    ai_response = call_gemini(prompt)
    return ai_response


def parse_questions_from_ai_text(raw_ai_text):
    """
    WHAT: Takes the AI's raw text response (from generate_assessment_paper)
    and splits it into a clean Python list of question dictionaries.

    WHY: The AI gives us back one big block of text. To DISPLAY each
    question nicely in Streamlit (in its own box, with its own type
    label, etc.), we need to break that text into separate, structured
    pieces. This function does that splitting/parsing work.

    HOW: We rely on the strict format we asked for in ai_prompts.py
    (each question separated by "---", with labeled fields).
    """
    questions = []

    # Split the AI's text wherever we see our "---" separator.
    raw_blocks = raw_ai_text.split("---")

    for block in raw_blocks:
        block = block.strip()
        if not block:
            continue  # Skip empty leftover chunks.

        # Set up default values in case a field is missing.
        question_data = {
            "type": "UNKNOWN",
            "question": "",
            "options": "N/A",
            "answer": ""
        }

        # Go through the block line by line and pick out labeled fields.
        lines = block.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith("TYPE:"):
                question_data["type"] = line.replace("TYPE:", "").strip()
            elif line.startswith("QUESTION:"):
                question_data["question"] = line.replace("QUESTION:", "").strip()
            elif line.startswith("OPTIONS:"):
                question_data["options"] = line.replace("OPTIONS:", "").strip()
            elif line.startswith("ANSWER:"):
                question_data["answer"] = line.replace("ANSWER:", "").strip()

        # Only keep this as a valid question if it actually has question text.
        if question_data["question"]:
            questions.append(question_data)

    return questions