import streamlit as st
from pypdf import PdfReader

from model import analyze_document, OllamaError


st.set_page_config(
    page_title="Legal Document Analyzer",
    page_icon="⚖️",
    layout="wide"
)

st.title("Automated Legal Document Analyzer")
st.write(
    "Analyze legal documents, extract important contract terms, "
    "identify key clauses, and generate a concise summary using "
    "Qwen3:4B through local Ollama."
)

st.info(
    "Educational use only. This tool does not provide legal advice. "
    "Always verify the results against the original document."
)

st.subheader("1. Provide a Legal Document")

uploaded_file = st.file_uploader(
    "Upload a legal document (optional)",
    type=["txt", "pdf"],
    help="Supported formats: TXT and PDF."
)

pasted_text = st.text_area(
    "Or paste the legal document text here",
    height=250,
    placeholder=(
        "Paste an employment agreement, rental agreement, "
        "NDA, service agreement, or another legal document..."
    )
)

st.caption(
    "If you upload a file, the uploaded file will be analyzed "
    "instead of the pasted text."
)

if st.button("Analyze Document", type="primary", use_container_width=True):
    document_text = ""

    # Read the uploaded file if one is provided.
    if uploaded_file is not None:
        try:
            if uploaded_file.name.lower().endswith(".txt"):
                document_text = uploaded_file.getvalue().decode(
                    "utf-8-sig"
                )

            elif uploaded_file.name.lower().endswith(".pdf"):
                reader = PdfReader(uploaded_file)

                if reader.is_encrypted:
                    st.error(
                        "This PDF is encrypted. Please upload an "
                        "unencrypted PDF or paste its text."
                    )
                    st.stop()

                pages = []

                for page in reader.pages:
                    pages.append(page.extract_text() or "")

                document_text = "\n\n".join(pages)

                if not document_text.strip():
                    st.error(
                        "No readable text was found in this PDF. "
                        "It may be a scanned document. Please paste "
                        "the text or use a text-based PDF."
                    )
                    st.stop()

        except UnicodeDecodeError:
            st.error(
                "Could not read the TXT file as UTF-8. "
                "Save it as a UTF-8 text file and try again."
            )
            st.stop()

        except Exception:
            st.error(
                "The uploaded file could not be read. "
                "Please check that it is a valid TXT or PDF file."
            )
            st.stop()

    else:
        document_text = pasted_text

    # Validate the extracted document.
    document_text = document_text.strip()

    if not document_text:
        st.warning(
            "Please paste legal document text or upload a file."
        )
        st.stop()

    if len(document_text) < 50:
        st.warning(
            "The document is very short. Please provide more text "
            "for a meaningful analysis."
        )
        st.stop()

    st.subheader("2. Document Information")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Characters", f"{len(document_text):,}")

    with col2:
        st.metric(
            "Estimated Words",
            f"{len(document_text.split()):,}"
        )

    st.subheader("3. Analysis Results")

    progress_bar = st.progress(0)
    status_text = st.empty()

    def update_progress(completed, total):
        progress_bar.progress(
            min(int(completed / total * 100), 100)
        )

        if completed < total:
            status_text.text(
                f"Analyzing document sections: "
                f"{completed} of {total - 1}"
            )
        else:
            status_text.text("Analysis completed.")

    try:
        with st.spinner(
            "Qwen3:4B is analyzing the document. "
            "Please wait..."
        ):
            result = analyze_document(
                document_text,
                progress_callback=update_progress
            )

        status_text.success("Document analysis completed.")

        st.markdown(result)

        st.download_button(
            label="Download Analysis Report",
            data=result,
            file_name="legal_document_analysis.txt",
            mime="text/plain",
            use_container_width=True
        )

        with st.expander("View Original Document Text"):
            st.text(document_text)

    except OllamaError as error:
        status_text.empty()
        progress_bar.empty()
        st.error(str(error))

    except Exception:
        status_text.empty()
        progress_bar.empty()
        st.error(
            "An unexpected error occurred. Please check your "
            "input, Ollama server, and model installation, "
            "then try again."
        )

st.divider()

st.caption(
    "Powered by Python, Streamlit, and Ollama with Qwen3:4B. "
    "The model runs locally on your computer."
)