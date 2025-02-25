
import os
import json
import base64
import io
from io import BytesIO
from langchain_community.document_loaders import PyPDFLoader

from utils.config import *
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_community.document_loaders.parsers.pdf import (
    PyMuPDFParser,
)
from langchain_core.document_loaders import BaseBlobParser, Blob
import logging

class BytesIOPyMuPDFLoader(PyMuPDFLoader):
    """Load `PDF` files using `PyMuPDF` from a BytesIO stream."""

    def __init__(
        self,
        pdf_stream: BytesIO,
        *,
        extract_images: bool = False,
        **kwargs,
    ) -> None:
        """Initialize with a BytesIO stream."""
        try:
            import fitz  # noqa:F401
        except ImportError:
            raise ImportError(
                "`PyMuPDF` package not found, please install it with "
                "`pip install pymupdf`"
            )
        # We don't call the super().__init__ here because we don't have a file_path.
        self.pdf_stream = pdf_stream
        self.extract_images = extract_images
        self.text_kwargs = kwargs

    def load(self, **kwargs):
        """Load file."""
        if kwargs:
            logging.warning(
                f"Received runtime arguments {kwargs}. Passing runtime args to `load`"
                f" is deprecated. Please pass arguments during initialization instead."
            )

        text_kwargs = {**self.text_kwargs, **kwargs}

        # Use 'stream' as a placeholder for file_path since we're working with a stream.
        blob = Blob.from_data(self.pdf_stream.getvalue(), path="stream")

        parser = PyMuPDFParser(
            text_kwargs=text_kwargs, extract_images=self.extract_images
        )

        return parser.parse(blob)

def process_LLM_response(response_str:str):
    response_str = response_str.replace("<think>", "---  \n**Thought Process**")
    response_str = response_str.replace("</think>", "---  \n**Response**")
    return response_str

def chat_response_parsing(from_ws):
    data = json.loads(from_ws["data"])
    msg = data["response"]
    state = data["state"]

    msg = process_LLM_response(msg)

    return msg, state

def process_user_query(from_user: str):
    # Load received query and model name
    recv_dict = json.loads(from_user)
    user_id = recv_dict["user_id"]
    query = recv_dict["query"]
    model = recv_dict["model"]
    context = recv_dict["context"]
    
    if query.startswith(CHAT_PROMPT_TEMPLATE_NAMES["coding"]):
        recv_dict["agent"] = "coding"
    elif query.startswith(CHAT_PROMPT_TEMPLATE_NAMES["translate"]):
        recv_dict["agent"] = "translate"
    elif query.startswith(CHAT_PROMPT_TEMPLATE_NAMES["summarize"]):
        recv_dict["agent"] = "summarize"
    elif query.startswith(CHAT_PROMPT_TEMPLATE_NAMES["file"]):
        recv_dict["agent"] = "file"
    else:
        recv_dict["agent"] = "general"
    
    return recv_dict

def process_context(context):
    fname, fdata_str = context["fname"], context["fdata"]
    file_extension, data_str = fdata_str.split(",")
    
    # Create directory for temp files
    if not os.path.exists(CHAT_TEMP_DIR):
        os.makedirs(CHAT_TEMP_DIR)
    
    if "pdf" in file_extension:
        return pdf_base64_to_document(data_str)
    
    else:
        return ""

def pdf_base64_to_document(base64_str):
    buffer = base64.b64decode(base64_str)

    with open("D://tmp//myfile.pdf", "wb") as f:
        f.write(buffer)

    loader = PyPDFLoader("myfile.pdf")

    return loader.load()