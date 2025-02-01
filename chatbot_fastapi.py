from fastapi import FastAPI, UploadFile, File, Form
import os
from chatbot import extract_content, query_gemini_api, extract_from_folder

app = FastAPI()

document_text = ""

@app.post("/upload_folder/")
async def upload_folder(folder_path: str = Form(...)):
    global document_text
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        return {"error": "Folder not found."}
    
    document_text = extract_from_folder(folder_path)
    if not document_text:
        return {"error": "No text extracted from the documents."}
    
    return {"message": "Documents processed successfully."}

@app.post("/query/")
async def query_chatbot(user_query: str = Form(...)):
    if not document_text:
        return {"error": "No text extracted. Please upload documents first."}
    
    response = query_gemini_api(document_text, user_query)
    return {"response": response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
