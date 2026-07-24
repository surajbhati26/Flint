# app.py
# ------------------------------------------------------------
# WHAT THIS FILE DOES:
# This is the MAIN file we run to start the app. It builds the
# entire user interface (UI) using Streamlit, and connects all our
# other files together (file_utils, ai_prompts, assessment_engine).
#
# WHY WE DO THIS:
# app.py is like the "control room" — it doesn't do heavy AI work
# or file-reading itself, it just calls the right helper functions
# from our other files and displays the results nicely on screen.
#
# HOW TO RUN THIS APP:
# In your terminal, type:  streamlit run app.py
# ------------------------------------------------------------

import streamlit as st
import assessment_engine
import file_utils
import config

# ------------------------------------------------------------
# BASIC PAGE SETUP
# ------------------------------------------------------------
st.set_page_config(page_title="EducatorAssessmentPro", layout="wide")

st.title("📚 EducatorAssessmentPro")
st.caption("An AI-powered assistant that helps educators create and grade assessments faster.")

# ------------------------------------------------------------
# SESSION STATE SETUP
# WHAT: "session_state" is Streamlit's way of remembering values
# (like variables) as the user clicks around the app, instead of
# forgetting everything every time the screen refreshes.
# WHY: Without this, every button click would erase our previously
# generated topics/questions, which would be a frustrating experience.
# ------------------------------------------------------------
if "extracted_topics" not in st.session_state:
    st.session_state.extracted_topics = ""

if "assessment_raw_text" not in st.session_state:
    st.session_state.assessment_raw_text = ""

if "parsed_questions" not in st.session_state:
    st.session_state.parsed_questions = []

if "all_evaluations" not in st.session_state:
    st.session_state.all_evaluations = []  # Will store text summaries of each graded answer.

# ------------------------------------------------------------
# CHECK IF THE API KEY IS SET UP BEFORE DOING ANYTHING ELSE
# ------------------------------------------------------------
if not config.is_api_key_configured():
    st.warning(
        "⚠️ You haven't added your Gemini API key yet! "
        "Open config.py and replace PASTE_YOUR_KEY_HERE with your real key "
        "from https://aistudio.google.com/app/apikey"
    )

# We organize the app into TABS — this keeps each feature (from the
# requirements) visually separated and easy for a teacher to navigate.
tab1, tab2, tab3, tab4 = st.tabs([
    "1️⃣ Upload & Topics",
    "2️⃣ Generate Assessment",
    "3️⃣ Evaluate Answers",
    "4️⃣ Class Report"
])

# ============================================================
# TAB 1: FILE UPLOAD + TOPIC DETECTION
# ============================================================
with tab1:
    st.header("Upload Study Material")
    st.write("Upload a PDF or TXT file. The AI will read it and summarize the core topics.")

    uploaded_file = st.file_uploader("Choose a file", type=["pdf", "txt"])

    if uploaded_file is not None:
        # Show a spinner so the teacher knows the app is working, not frozen.
        with st.spinner("Reading your document..."):
            document_text = file_utils.get_document_text(uploaded_file)

        # If our file reader returned an error message, show it clearly.
        if document_text.startswith("ERROR:"):
            st.error(document_text)
        else:
            st.success("File read successfully!")

            # Let the teacher preview the raw extracted text if curious.
            with st.expander("Preview extracted text"):
                st.text(document_text[:2000] + ("..." if len(document_text) > 2000 else ""))

            if st.button("🔍 Extract Topics with AI"):
                if not assessment_engine.configure_gemini():
                    st.error("AI is not configured. Please check your API key in config.py.")
                else:
                    with st.spinner("AI is analyzing the document..."):
                        topics_result = assessment_engine.extract_topics_from_document(document_text)
                    st.session_state.extracted_topics = topics_result

    # Display the extracted topics if we have them.
    if st.session_state.extracted_topics:
        st.subheader("📝 AI-Generated Summary & Topics")
        st.markdown(st.session_state.extracted_topics)

# ============================================================
# TAB 2: QUESTION GENERATION WITH DIFFICULTY SELECTION
# ============================================================
with tab2:
    st.header("Generate Assessment Paper")

    if not st.session_state.extracted_topics:
        st.info("👈 First upload a document and extract topics in Tab 1.")
    else:
        st.write("Using the topics extracted earlier, choose a difficulty level and generate questions.")

        # This is our REQUIRED difficulty selector (a slider-like dropdown).
        difficulty = st.select_slider(
            "Select Difficulty Level",
            options=["Easy", "Medium", "Hard"],
            value="Medium"
        )

        if st.button("✨ Generate Assessment"):
            if not assessment_engine.configure_gemini():
                st.error("AI is not configured. Please check your API key in config.py.")
            else:
                with st.spinner("AI is writing your assessment paper... this may take a moment."):
                    raw_result = assessment_engine.generate_assessment_paper(
                        st.session_state.extracted_topics, difficulty
                    )
                st.session_state.assessment_raw_text = raw_result
                # Convert the AI's raw text into a clean list of question dictionaries.
                st.session_state.parsed_questions = assessment_engine.parse_questions_from_ai_text(raw_result)

    # Display the generated, organized questions.
    if st.session_state.parsed_questions:
        st.subheader("📄 Generated Assessment Paper")
        for i, q in enumerate(st.session_state.parsed_questions, start=1):
            with st.container(border=True):
                st.markdown(f"**Q{i} ({q['type']})**")
                st.write(q["question"])
                if q["options"] != "N/A":

                    st.write(q["options"])
                with st.expander("Show model answer"):
                    st.write(q["answer"])

# ============================================================
# TAB 3: EVALUATION & SCORING
# ============================================================
with tab3:
    st.header("Evaluate a Student's Answer")
    st.write("Paste a short-answer question and a student's response to get an AI-suggested score and feedback.")

    # We let the teacher pick from previously generated short-answer
    # questions if available, or type their own question manually.
    question_options = ["(Type my own question)"]
    short_answer_questions = [
        q["question"] for q in st.session_state.parsed_questions
        if q["type"] == "SHORT_ANSWER"
    ]
    question_options += short_answer_questions

    selected_question_option = st.selectbox("Select a question", question_options)

    if selected_question_option == "(Type my own question)":
        question_text = st.text_area("Enter the question text")
    else:
        question_text = selected_question_option
        st.write(f"**Selected Question:** {question_text}")

    student_answer = st.text_area("Paste the student's answer here")

    if st.button("📊 Evaluate Answer"):
        if not question_text or not student_answer:
            st.warning("Please provide both a question and a student answer.")
        elif not assessment_engine.configure_gemini():
            st.error("AI is not configured. Please check your API key in config.py.")
        else:
            with st.spinner("AI is grading the answer..."):
                evaluation_result = assessment_engine.evaluate_student_answer(question_text, student_answer)

            st.subheader("AI Evaluation Result")
            st.markdown(evaluation_result)

            # Save this evaluation so it can be included in the class-wide report later.
            st.session_state.all_evaluations.append(
                f"Question: {question_text}\nStudent Answer: {student_answer}\n{evaluation_result}\n"
            )
            st.success("Saved this evaluation to the class report (see Tab 4).")

# ============================================================
# TAB 4: REPORTS & CLASS-WIDE FEEDBACK
# ============================================================
with tab4:
    st.header("Class Report & Aggregated Feedback")

    if st.session_state.assessment_raw_text:
        st.subheader("📄 Full Assessment Paper (Raw)")
        with st.expander("View full generated assessment text"):
            st.text(st.session_state.assessment_raw_text)

    if not st.session_state.all_evaluations:
        st.info("No evaluations yet. Go to Tab 3 to evaluate some student answers first.")
    else:
        st.write(f"You have {len(st.session_state.all_evaluations)} saved evaluation(s).")

        if st.button("📈 Generate Class-Wide Feedback Summary"):
            if not assessment_engine.configure_gemini():
                st.error("AI is not configured. Please check your API key in config.py.")
            else:
                # Combine all individual evaluations into one big text block
                # to send to the AI for pattern-finding across the whole class.
                combined_evaluations_text = "\n\n---\n\n".join(st.session_state.all_evaluations)

                with st.spinner("AI is summarizing feedback across all evaluations..."):
                    class_summary = assessment_engine.aggregate_class_feedback(combined_evaluations_text)

                st.subheader("🏫 Class-Wide Performance Summary")
                st.markdown(class_summary)

        with st.expander("View raw evaluation history"):
            for idx, evaluation in enumerate(st.session_state.all_evaluations, start=1):
                st.text(f"Evaluation #{idx}\n{evaluation}")