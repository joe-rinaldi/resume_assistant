from io import BytesIO
from pathlib import Path

import pymupdf
from docx import Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from google.genai import types
from google.adk import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest


SUPPORTED_DOCUMENT_TYPES = {
    ".docx": (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ),
    ".pdf": "application/pdf",
    ".txt": "text/plain",
}


def _document_extension(filename: str, mime_type: str) -> str | None:
    extension = Path(filename).suffix.lower()
    if extension in SUPPORTED_DOCUMENT_TYPES:
        return extension

    return next(
        (
            supported_extension
            for supported_extension, supported_mime_type in SUPPORTED_DOCUMENT_TYPES.items()
            if mime_type.lower() == supported_mime_type
        ),
        None,
    )


def _extract_document_text(data: bytes, extension: str) -> str:
    if extension == ".pdf":
        with pymupdf.open(stream=data, filetype="pdf") as document:
            return "\n".join(page.get_text() for page in document)

    if extension == ".docx":
        document = Document(BytesIO(data))
        content = []
        for item in document.iter_inner_content():
            if isinstance(item, Paragraph):
                content.append(item.text)
            elif isinstance(item, Table):
                content.extend(
                    "\t".join(cell.text for cell in row.cells)
                    for row in item.rows
                )
        return "\n".join(content)

    if extension == ".txt":
        try:
            return data.decode("utf-8-sig")
        except UnicodeDecodeError:
            return data.decode("cp1252")

    raise ValueError(f"Unsupported document extension: {extension}")


def extract_uploaded_documents(
    _context: CallbackContext, request: LlmRequest
) -> None:
    for content in request.contents:
        if content.role != "user" or not content.parts:
            continue

        updated_parts = []
        changed = False
        for part in content.parts:
            inline_data = part.inline_data
            file_data = part.file_data
            if inline_data:
                filename = inline_data.display_name or "uploaded document"
                mime_type = inline_data.mime_type or ""
                extension = _document_extension(filename, mime_type)
                if extension:
                    if not isinstance(inline_data.data, bytes):
                        raise ValueError(
                            f"Document upload {filename!r} has no readable data."
                        )
                    text = _extract_document_text(inline_data.data, extension)
                    if not text.strip():
                        raise ValueError(
                            f"No text could be extracted from {filename!r}."
                        )
                    updated_parts.append(
                        types.Part(
                            text=f"[Extracted text from {filename}]\n{text}"
                        )
                    )
                    changed = True
                    continue
            elif file_data:
                filename = (
                    file_data.display_name
                    or file_data.file_uri
                    or "uploaded document"
                )
                if _document_extension(filename, file_data.mime_type or ""):
                    raise ValueError(
                        f"Cannot extract {filename!r}: the uploaded document "
                        "does not contain inline file data."
                    )

            updated_parts.append(part)

        if changed:
            content.parts = updated_parts



root_agent = Agent(
    name="resume_assistant",
    model="gemini-3.5-flash-lite",
    description="Resume Assistant tool",
    instruction="""
    You are a professional recruiting assistant.

    When the user attaches a resume and a job description, they can be PDF, DOCX, or TXT.
    PDF and DOCX uploads are converted to plain text before analysis; TXT uploads are
    passed through as text.
    You will perform the following tasks:

STEP 1:
extract all text from both documents.

STEP 2:
Identify:
- Technical Skills
- Frameworks
- Programming Languages
- Databases
- Cloud Technologies
- Certifications
- Soft Skills

STEP 3:
Compare resume skills against job requirements.

STEP 4:
Return following information as a json object with the following keys:

1. Match Percentage
2. Missing Skills
3. Strengths
4. Interview Recommendations
5. Resume Improvement Suggestions

""",
    #generate_content_config=types.GenerateContentConfig(
    #    max_output_tokens=30000
    #),
    before_model_callback=extract_uploaded_documents,
)