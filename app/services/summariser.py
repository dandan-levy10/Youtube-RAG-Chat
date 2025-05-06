from langchain_ollama import OllamaLLM
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

llm = OllamaLLM(
    model="llama3.2:latest",
    model_kwargs={
        "max_tokens": 16000,
        "temperature": 0.0,
    }
    )

def summarise_documents(documents):
    chain = load_summarize_chain(llm=llm, chain_type="stuff")
    summary = chain.invoke(input=documents)
    logger.info(f"Summarised transcript from video '{documents[0].metadata["title"]}'  documents using '{chain._chain_type}' chain type")
    logger.debug(f"Summary: {summary["output_text"]}")
    
    return summary["output_text"]

def length_function(documents: list[Document]) -> int:
    """Get number of tokens for input contents."""
    length = sum(llm.get_num_tokens(doc.page_content) for doc in documents)
    char_length = sum(len(doc.page_content) for doc in documents)
    logger.info(f"Total documents token length: {length}, char length {char_length}")
    # logger.info(f"Max input size: {llm.max_input_size}")
    return length 
