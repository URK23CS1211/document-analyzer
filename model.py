import requests

from prompt import create_analysis_prompt, create_combination_prompt


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3:4b"

# Maximum number of characters in one document section.
CHUNK_SIZE = 6000

# Documents with more than this many characters are split.
SINGLE_REQUEST_LIMIT = 9000


class OllamaError(Exception):
    """Raised when Ollama cannot complete a request."""


def split_into_chunks(text, chunk_size=CHUNK_SIZE):
    """
    Split text into smaller sections, preferring paragraph boundaries.
    """

    chunks = []
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))

        if end < len(text):
            boundary = text.rfind("\n", start, end)

            # Avoid creating extremely small chunks.
            if boundary > start + chunk_size // 2:
                end = boundary

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start = end

    return chunks


def generate_response(prompt, num_predict=900):
    """
    Send a prompt to the locally running Ollama server.
    """

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "think": False,
        "options": {
            "temperature": 0.2,
            "num_predict": num_predict
        }
    }

    try:
        response = requests.post(
            OLLAMA_URL,
            json=payload,
            timeout=240
        )

    except requests.exceptions.Timeout as exc:
        raise OllamaError(
            "Ollama took too long to respond. Try a shorter document "
            "or wait for the model to finish loading."
        ) from exc

    except requests.exceptions.ConnectionError as exc:
        raise OllamaError(
            "Cannot connect to Ollama. Make sure Ollama is installed "
            "and running on http://localhost:11434."
        ) from exc

    except requests.exceptions.RequestException as exc:
        raise OllamaError(
            "A network error occurred while contacting Ollama."
        ) from exc

    if response.status_code == 404:
        raise OllamaError(
            f"The model '{MODEL_NAME}' may not be installed. "
            f"Run: ollama pull {MODEL_NAME}"
        )

    if not response.ok:
        try:
            details = response.json().get("error", "")
        except ValueError:
            details = ""

        raise OllamaError(
            f"Ollama returned HTTP {response.status_code}. "
            f"{details or 'Check the Ollama installation and model.'}"
        )

    try:
        data = response.json()
    except ValueError as exc:
        raise OllamaError(
            "Ollama returned an invalid response."
        ) from exc

    result = data.get("response", "").strip()

    if not result:
        raise OllamaError(
            "The model returned an empty response. Please try again."
        )

    return result


def analyze_document(document_text, progress_callback=None):
    """
    Analyze a complete document and return a consolidated report.
    """

    document_text = document_text.strip()

    if not document_text:
        raise OllamaError(
            "The document is empty. Please provide readable text."
        )

    if len(document_text) <= SINGLE_REQUEST_LIMIT:
        prompt = create_analysis_prompt(document_text)

        if progress_callback:
            progress_callback(1, 1)

        return generate_response(prompt, num_predict=1400)

    chunks = split_into_chunks(document_text)
    chunk_analyses = []

    for index, chunk in enumerate(chunks):
        prompt = create_analysis_prompt(chunk)

        analysis = generate_response(prompt, num_predict=900)
        chunk_analyses.append(analysis)

        if progress_callback:
            progress_callback(index + 1, len(chunks) + 1)

    combination_prompt = create_combination_prompt(chunk_analyses)

    final_report = generate_response(
        combination_prompt,
        num_predict=1800
    )

    if progress_callback:
        progress_callback(len(chunks) + 1, len(chunks) + 1)

    return final_report