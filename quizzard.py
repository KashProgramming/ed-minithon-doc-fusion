import re
import os
import google.generativeai as genai
from file_handler.docx_handler import extract_docx_content
from file_handler.ppt_handler import extract_pptx_content
from file_handler.pdf_handler import extract_pdf_content

def extract_content(file_path):
    """Extracts text from a given document based on its file type."""
    try:
        # Skip temporary or system files starting with '~$'
        if os.path.basename(file_path).startswith("~$"):
            print(f"Skipping temporary file: {file_path}")
            return {"text":[], "images": [], "tables": []}  # Return empty string if it's a temp file
        file_type = file_path.split(".")[-1].lower()
        if file_type == "pdf":
            return extract_pdf_content(file_path)
        elif file_type == "docx":
            return extract_docx_content(file_path)
        elif file_type == "pptx":
            return extract_pptx_content(file_path)
        else:
            return {"text":[], "images": [], "tables": []}  # Ignore unsupported files
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return {"text":[], "images": [], "tables": []}  # Return empty string on error

def extract_from_folder(folder_path):
    """Extracts content from all valid files in a given folder."""
    all_text = ""
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.lower().endswith((".pdf", ".docx", ".pptx")):
            print(f"Processing: {file_name} ...")
            text = extract_content(file_path)["text"]
            for page_text in text:
                if page_text.strip():
                    all_text += f"\n\n=== {file_name} ===\n{page_text}"
    print(all_text)
    return all_text.strip()

genai.configure(api_key="API_KEY")

def query_gemini_api(document_text, user_query):
    prompt = f"Based on the following document:\n\n{document_text}\n\n{user_query}"
    
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)

    return response.text if response else "No response from Gemini."

def parse_mcq_output(mcq_text):
    question_pattern = re.findall(r"(\d+)\.\s(.*?)\n\s*a\)\s(.*?)\n\s*b\)\s(.*?)\n\s*c\)\s(.*?)\n\s*d\)\s(.*?)\n",mcq_text,re.DOTALL)

    questions_dict = {
        num: {
            "question": question.strip(),
            "options": {
                "a": option_a.strip(),
                "b": option_b.strip(),
                "c": option_c.strip(),
                "d": option_d.strip()
            }
        }
        for num, question, option_a, option_b, option_c, option_d in question_pattern
    }

    answer_pattern = re.search(r"\{(.*?)\}", mcq_text, re.DOTALL)
    answers_dict = {}
    if answer_pattern:
        answer_text = answer_pattern.group(1)
        answer_entries = re.findall(r'"(\d+)":\s*"([a-d])"', answer_text)
        answers_dict = {num: ans for num, ans in answer_entries}

    return questions_dict, answers_dict

def chatbot():
    file_path = r"C:\Users\Megh\Desktop\sample\sample.pdf"  # Replace with your actual PDF file path
    
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        print("Error: File not found.")
        return
    
    print("Processing.....\nYour quizzard will be live any moment")

    document_text = extract_text_from_pdf(file_path)
    
    if not document_text:
        print("Error: No text extracted from the document.")
        return

    print("\nDocument processed. Generating MCQs...")
    
    user_query = ("Based on the following document:\n\n"
                  f"{document_text}\n\n"
                  "Generate 10 multiple-choice questions (MCQs) from this document. \n\n"
                  "Format the output exactly as follows:\n\n"
                  "### Questions:\n"
                  "1. Question text here?\n"
                  "   a) Option 1\n"
                  "   b) Option 2\n"
                  "   c) Option 3\n"
                  "   d) Option 4\n\n"
                  "2. Question text here?\n"
                  "   a) Option 1\n"
                  "   b) Option 2\n"
                  "   c) Option 3\n"
                  "   d) Option 4\n\n"
                  "...(repeat for 10 questions)\n\n"
                  "### Answers:\n"
                  "{ \"1\": \"b\", \"2\": \"d\", \"3\": \"a\", ..., \"10\": \"c\" }\n\n"
                  "Ensure that:\n"
                  "- Each question has 4 answer choices labeled (a, b, c, d).\n"
                  "- The correct answer should be provided in a JSON dictionary format separately.\n"
                  "- Do not add extra text, explanations, or formatting beyond the requested structure.\n\n"
                  "Return only the questions and answers in the specified format.")

    mcq_output = query_gemini_api(document_text, user_query)

    questions, answers = parse_mcq_output(mcq_output)

    print("\nExtracted Questions Dictionary:\n", questions)
    print("\nExtracted Answers Dictionary:\n", answers)

if __name__ == "__main__":
    chatbot()
