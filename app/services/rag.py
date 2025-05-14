from app.services.embedding import get_embedding_function
from langchain_ollama import OllamaLLM
from langchain.vectorstores import VectorStore
from langchain_chroma.vectorstores import Chroma
import logging

from app.services.transcription import get_transcript, extract_video_id
from app.services.chunking import chunk_documents
from app.services.embedding import embed_and_save

logger = logging.getLogger(__name__)

class ChatMemory:
    def __init__(self, max_turns=5):
        self.max_turns = max_turns
        self.buffer = [] # list of (user, assistant) tuples

    def append(self, user_message: str, assistant_message: str):
        self.buffer.append((user_message, assistant_message))
        logger.debug(f"Appended (user_message, assistant_message) tuple to memory")

        if len(self.buffer) > self.max_turns:
            self.buffer.pop(0)
            logger.debug("Memory buffer capacity exceeded {self.max_turns}, removed oldest message")

    def to_prompt(self):
        history = [f"User: {u}; \nAssistant: {a}" for u, a in self.buffer]
        logger.debug(f"ChatMemory.to_prompt called. History: {history}")
        return "\n\n".join(history)

class TranscriptRetriever:
    def __init__(self, vector_store: VectorStore, k=4): 
        self.retriever = vector_store.as_retriever(
            search_type= "mmr",
            search_kwargs={"k":k}
        )
        logger.info(f"Initialised TranscriptReciever with vector store {vector_store.__repr__}, {k} retrival context chunks")

    def get_context(self, query: str) -> str:
        logger.debug(f"get_context received query of type {type(query)}, {query}")
        try:
            results = self.retriever.get_relevant_documents(query=query)
        except Exception:
            logger.error("Failed calling get_relevant_documents with query=%r", query, exc_info=True)
            raise

        context = "\n\n".join(result.page_content for result in results)
        logger.debug(f"TranscriptReciever.get_context called. Context: {context}")

        return context
        
class ChatSession:
    def __init__(self, llm, vectordb, retriever: TranscriptRetriever, memory: ChatMemory, prompt_template: str):
        self.llm = llm
        self.vectorstore = vectordb
        self.retriever = retriever
        self.memory = memory
        self.prompt_template = prompt_template
        logger.debug(f"ChatSession initialised with {llm.__str__}, retriever {retriever.__str__}, memory {memory.__str__}")

    def ask(self, question: str, history: list[tuple[str,str]]) -> str:
        # 1) Retrieve context
        context = self.retriever.get_context(query = question)

        # logger.debug(f"Excerpt: {context}")

        # 2) Build the prompt
        prompt_blocks = []

        prompt_blocks.append(self.prompt_template)
        
        history = history_to_prompt(history)

        if history:
            prompt_blocks.append(history)

        prompt_blocks.append(f"User: {question} \n\n")

        prompt_blocks.append(f"Relevant context: \n\n {context} \n\n")

        prompt_blocks.append(f"Assistant: \n")

        prompt = "\n".join(prompt_blocks)
        logger.debug(f"Prompt: {prompt}")

        # 3) Call the LLM
        result = self.llm.generate([prompt])
        logger.info(f"LLM called. Result: {result}")
        answer = result.generations[0][0].text
        logger.info(f"LLM answer text: {answer}")

        # 4) Update memory
        # self.memory.append(user_message=question, assistant_message=answer)

        return answer


prompt_starter = "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise."

def create_chat_session():
    # (1) instantiate your pieces
    memory    = ChatMemory(max_turns=5)
    embedding_function = get_embedding_function()
    vectordb = Chroma(
        embedding_function= embedding_function,
        persist_directory="app/chroma_db"
        )
    retriever = TranscriptRetriever(vector_store=vectordb, embedding_fn=embedding_function, k=6)
    llm       = OllamaLLM(model="llama3.2")

    # (2) create a session
    session = ChatSession(llm=llm, vectordb=vectordb, retriever=retriever, memory=memory, prompt_template= prompt_starter)
    return session

def has_documents_for(video_id: str, vectordb) -> bool:
    return bool(vectordb.get(filter={"video_id": video_id}))

def history_to_prompt(history: list[tuple[str,str]]):
    history = [f"User: {u}\n Assistant: {a}" for u, a in history]
    return "\n\n".join(history)

def rag_chat_service(video_url: str, question: str, history: list[tuple[str,str]]) -> str:
    # extract video_id
    video_id = extract_video_id(video_url=video_url)
    # create chat session
    session = create_chat_session()
    # if not video_id exists in vectordb
    if not has_documents_for(video_id=video_id, vectordb=session.vectorstore):
        # retrieve transcript
        documents = get_transcript(video_url=video_url)
        # chunk transcript
        chunks = chunk_documents(documents, chunk_size= 800, chunk_overlap= 50)
        # embed chunks, upload to vectordb
        embed_and_save(chunks)
    
    answer = session.ask(question=question, history = history)
    return answer