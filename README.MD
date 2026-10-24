# Experiment 5: Automated Legal Document Analyzer

## 1. Project Objective

To develop a simple AI-powered legal document analyzer using
Python, Streamlit, and the Qwen3:4B model running locally through
Ollama.

The application demonstrates legal document summarization,
information extraction, key clause identification, and basic
long-document chunking.

## 2. What the Application Does

The application allows a user to paste legal document text or
upload a TXT/PDF file.

It uses a locally running language model to identify:

- Document type
- Parties involved
- Purpose of the document
- Duration
- Key obligations
- Payment terms
- Termination conditions
- Important dates
- Confidentiality requirements
- Liability provisions
- Intellectual property clauses
- Dispute resolution
- Governing law
- Potentially important clauses
- Missing or unclear information
- Concise summary

The generated analysis can be downloaded as a text report.

## 3. Technologies Used

- Python
- Streamlit
- Ollama
- Qwen3:4B
- Requests
- pypdf

No OpenAI API key, database, vector database, or cloud LLM API
is required.

## 4. Project Structure

experiment5_legal_analyzer/
|
|-- app.py
|-- model.py
|-- prompt.py
|-- requirements.txt
|-- README.md

## 5. How the System Works

1. The user pastes text or uploads a TXT/PDF document.
2. Python extracts the document text.
3. The prompt module creates analysis instructions.
4. The model module sends the prompt to the local Ollama API.
5. Ollama runs the Qwen3:4B model and generates a response.
6. Long documents are divided into smaller sections.
7. The section analyses are combined into a final report.
8. Streamlit displays the report and provides a download option.

## 6. Install Ollama

Install Ollama for Windows from:

https://ollama.com/download

Open PowerShell and check the installation:

```powershell
ollama --version