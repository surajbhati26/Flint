# file_utils.py
# ------------------------------------------------------------
# WHAT THIS FILE DOES:
# This file's only job is reading uploaded files (PDF or TXT) and
# turning them into plain text that we can send to the AI.
#
# WHY WE DO THIS:
# Streamlit lets educators upload files, but an uploaded file starts
# out as raw bytes, not readable text. We need "translator" functions
# that convert PDFs and text files into a normal Python string.
# Keeping this logic in its own file (instead of mixing it into app.py)
# makes the code easier to test and understand.
# ------------------------------------------------------------

import PyPDF2


def extract_text_from_pdf(uploaded_file):
    """
    WHAT: Reads a PDF file (uploaded through Streamlit) and pulls out
    all the readable text, page by page.

    WHY: PDFs are not plain text by default — they're a special format.
    The PyPDF2 library knows how to "open the box" and read what's inside.

    HOW: We loop through every page in the PDF and glue the text together
    into one big string, separated by newlines so it stays readable.
    """
    text_chunks = []  # We'll collect each page's text here.

    try:
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text()
            # Some PDF pages (like scanned images) have no extractable text.
            # We check for that so we don't accidentally add "None" to our string.
            if page_text:
                text_chunks.append(page_text)
    except Exception as error:
        # If something goes wrong (corrupted file, weird format, etc.),
        # we don't want the whole app to crash. We return an error message
        # instead, which the UI can show to the user.
        return f"ERROR: Could not read PDF file. Details: {error}"

    full_text = "\n".join(text_chunks)

    if not full_text.strip():
        # This means the PDF had no readable text at all
        # (common with scanned/image-only PDFs).
        return "ERROR: No readable text found in this PDF. It may be a scanned image."

    return full_text


def extract_text_from_txt(uploaded_file):
    """
    WHAT: Reads a plain .txt file uploaded through Streamlit.

    WHY: Text files are simpler than PDFs, but Streamlit gives us the file
    as "bytes" (raw computer data), so we still need to convert it into
    a normal readable string using .decode().
    """
    try:
        raw_bytes = uploaded_file.read()
        text = raw_bytes.decode("utf-8")
        return text
    except Exception as error:
        return f"ERROR: Could not read text file. Details: {error}"


def get_document_text(uploaded_file):
    """
    WHAT: This is the "traffic cop" function. It looks at the uploaded
    file's name/extension and decides which specific reader function
    (PDF or TXT) to use.

    WHY: This lets the rest of our app just call ONE simple function
    ("get_document_text") without needing to know or care whether the
    file was a PDF or a TXT. This is called "abstraction" — hiding
    complicated details behind a simple, easy-to-use function.
    """
    if uploaded_file is None:
        return "ERROR: No file was uploaded."

    filename = uploaded_file.name.lower()

    if filename.endswith(".pdf"):
        return extract_text_from_pdf(uploaded_file)
    elif filename.endswith(".txt"):
        return extract_text_from_txt(uploaded_file)
    else:
        return "ERROR: Unsupported file type. Please upload a .pdf or .txt file."