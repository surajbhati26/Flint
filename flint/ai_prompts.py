


def build_topic_extraction_prompt(document_text):
    """
    WHAT: Builds the instruction we send to the AI to summarize a
    document and extract its core topics.

    WHY: We ask the AI to reply in a very specific, predictable format
    (a simple bulleted list) so our app can easily display it, and so
    later steps (question generation) know exactly what topics exist.
    """
    prompt = f"""
You are an expert educational content analyst.

Read the study material provided below and do two things:
1. Write a short summary (3-5 sentences) of what this material is about.
2. List the 5-8 core topics/concepts covered, as a simple bulleted list.

Format your response EXACTLY like this, with no extra commentary:

SUMMARY:
<your summary here>

TOPICS:
- <topic 1>
- <topic 2>
- <topic 3>
(etc.)

STUDY MATERIAL:
\"\"\"
{document_text}
\"\"\"
"""
    return prompt


def build_question_generation_prompt(topics_text, difficulty, num_mcq=3, num_short=2, num_essay=1):
    """
    WHAT: Builds the instruction we send to the AI to generate a full
    assessment paper (MCQs, short answers, essay prompts) based on
    the extracted topics and the chosen difficulty level.

    WHY: We are very specific about the exact output format (using
    clear labels like "Q1:", "TYPE:", "ANSWER:") so that our Python
    code can later split the AI's text response into separate,
    organized questions. This avoids messy AI output.

    PARAMETERS:
    - topics_text: the list of topics (as a string) from the previous step.
    - difficulty: "Easy", "Medium", or "Hard" — chosen by the educator.
    - num_mcq / num_short / num_essay: how many of each question type to create.
    """
    prompt = f"""
You are an expert exam-paper creator for teachers.

Create an assessment paper based on these topics:
{topics_text}

Difficulty level requested: {difficulty}

Create exactly:
- {num_mcq} Multiple Choice Questions (MCQ)
- {num_short} Short Answer Questions
- {num_essay} Essay-style Question(s)

FORMAT RULES (follow exactly, this is very important):
For every question, use this structure:

Q<number>:
TYPE: <MCQ / SHORT_ANSWER / ESSAY>
QUESTION: <the question text>
OPTIONS: <only for MCQ - list A) B) C) D) options, otherwise write "N/A">
ANSWER: <the correct answer or a strong model answer>
---

Make sure MCQs have exactly 4 options labeled A) B) C) D), with only
one correct answer. Make sure difficulty matches the requested level:
"Easy" means recall/basic understanding, "Medium" means applying
concepts, "Hard" means analysis or multi-step reasoning.

Do not add any text before Q1 or after the final "---".
"""
    return prompt


def build_evaluation_prompt(question_text, student_answer):
    """
    WHAT: Builds the instruction we send to the AI to grade a single
    student's short-answer response and give structured feedback.

    WHY: Teachers need consistency. By forcing a strict output format
    (a numeric score + separate feedback sections), we make sure every
    evaluation looks the same and can be displayed neatly in our app.
    """
    prompt = f"""
You are a fair and experienced teacher grading a student's answer.

QUESTION:
{question_text}

STUDENT'S ANSWER:
{student_answer}

Grade this answer on a scale of 0 to 10, where 10 means a perfect,
complete answer and 0 means completely incorrect or blank.

Respond EXACTLY in this format:

SCORE: <a number from 0 to 10>
STRENGTHS: <1-2 sentences on what the student did well>
IMPROVEMENTS: <1-2 sentences on what is missing or incorrect>
SUGGESTION: <one practical tip to help the student improve>
"""
    return prompt


def build_feedback_aggregation_prompt(list_of_evaluations_text):
    """
    WHAT: Builds the instruction we send to the AI to summarize
    feedback across MANY student evaluations into class-wide insights.

    WHY: A teacher grading 30 students doesn't want to read 30 separate
    reports one by one to find patterns. This prompt asks the AI to
    find COMMON strengths and weaknesses across the whole class,
    saving the teacher significant time (this directly matches our
    "saves time for educators" core goal).
    """
    prompt = f"""
You are an experienced teacher preparing a class performance summary
for a school report.

Below are individual evaluation results for multiple students on the
same assessment. Each entry includes a score and feedback notes.

EVALUATIONS:
{list_of_evaluations_text}

Based on ALL of these evaluations together, write a class-wide summary
with this exact structure:

OVERALL_PERFORMANCE: <1-2 sentence summary of how the class did overall>
COMMON_STRENGTHS: <bulleted list of things many students did well>
COMMON_WEAKNESSES: <bulleted list of things many students struggled with>
RECOMMENDED_NEXT_STEPS: <2-3 concrete suggestions for what to re-teach or reinforce>
"""
    return prompt