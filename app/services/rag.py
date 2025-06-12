import logging

from langchain.vectorstores import VectorStore
from langchain_chroma.vectorstores import Chroma
from langchain_ollama import OllamaLLM
from langchain.schema import Document
from sqlmodel import Session

from app.services.chunking import chunk_documents
from app.services.embedding import embed_and_save
from app.services.transcription import extract_video_id, get_transcript
from app.vector_database import get_embedding_function, get_vector_store, check_if_vectors_exist

logger = logging.getLogger(__name__)

class ChatMemory:
    def __init__(self, max_turns: int=5) -> None:
        self.max_turns = max_turns
        self.buffer: list[tuple[str, str]] = [] # list of (user, assistant) tuples

    def append(self, user_message: str, assistant_message: str) -> None:
        self.buffer.append((user_message, assistant_message))
        logger.debug("Appended (user_message, assistant_message) tuple to memory")

        if len(self.buffer) > self.max_turns:
            self.buffer.pop(0)
            logger.debug("Memory buffer capacity exceeded {self.max_turns}, removed oldest message")

    def to_prompt(self) -> str:
        history = [f"User: {u}; \nAssistant: {a}" for u, a in self.buffer]
        logger.debug(f"ChatMemory.to_prompt called. History: {history}")
        return "\n\n".join(history)

class TranscriptRetriever:
    def __init__(self, vector_store: VectorStore, k: int=4) -> None:
        self.vector_store = vector_store 
        self.k = k
        # retriever = vector_store.as_retriever(
        #     search_type= "mmr",
        #     search_kwargs={"k":k}
        # )
        # logger.info(f"Initialised TranscriptReciever with vector store {vector_store.__repr__}, {k} retrival context chunks")

    def get_context(self, query: str, video_id: str) -> str:
        logger.debug(f"get_context received query of type {type(query)}, {query}")
        try:
            retriever = self.vector_store.as_retriever(
                search_kwargs={
                    "k": self.k,
                    "filter": {"video_id": video_id}
                }
            )
            results = retriever.invoke(input=query)
        except Exception:
            logger.error("Failed calling get_relevant_documents with query=%r", query, exc_info=True)
            raise

        context = "\n\n".join(result.page_content for result in results)
        logger.debug(f"TranscriptReciever.get_context called. Context: \n\n{context}")

        return context
        
class ChatSession:
    def __init__(self, llm: OllamaLLM, vectordb: Chroma, retriever: TranscriptRetriever, memory: ChatMemory, prompt_template: str) -> None:
        self.llm = llm
        self.vectorstore = vectordb
        self.retriever = retriever
        self.memory = memory
        self.prompt_template = prompt_template
        logger.debug(f"ChatSession initialised with {llm.__str__}, retriever {retriever.__str__}, memory {memory.__str__}")

    def ask(self, question: str, history: list[tuple[str,str]], video_id: str) -> str:
        # 1) Retrieve context
        context = self.retriever.get_context(query = question, video_id= video_id)

        # logger.debug(f"Excerpt: {context}")

        # 2) Build the prompt
        prompt_blocks = []

        prompt_blocks.append(self.prompt_template)
        
        history_as_prompt: str = history_to_prompt(history)

        if history:
            prompt_blocks.append(history_as_prompt)

        prompt_blocks.append(f"User: {question} \n\n")

        prompt_blocks.append(f"Relevant context: \n\n {context} \n\n")

        prompt_blocks.append("Assistant: \n")

        prompt = "\n".join(prompt_blocks)
        logger.debug(f"Prompt: {prompt}")

        # 3) Call the LLM
        result = self.llm.generate([prompt])
        logger.info(f"LLM called. Result: {result}")
        answer = result.generations[0][0].text
        # logger.info(f"LLM answer text: {answer}")

        # 4) Update memory
        # self.memory.append(user_message=question, assistant_message=answer)

        return answer


prompt_starter = "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If the context provided doesn't provide an answer to the question, just say that you don't know. Use three sentences maximum and keep the answer concise."

def create_chat_session() -> ChatSession:
    # (1) instantiate your pieces
    memory    = ChatMemory(max_turns=5)
    embedding_function = get_embedding_function()
    vectordb = get_vector_store(embedding_function)
    retriever = TranscriptRetriever(vector_store=vectordb, k=6)
    llm       = OllamaLLM(model="llama3.2")

    # (2) create a session
    session = ChatSession(llm=llm, vectordb=vectordb, retriever=retriever, memory=memory, prompt_template= prompt_starter)
    logger.debug("Chat session created.")
    return session

def history_to_prompt(history: list[tuple[str,str]]) -> str:
    history_chunks = [f"User: {u}\n Assistant: {a}" for u, a in history]
    return "\n\n".join(history_chunks)

def rag_chat_service(video_url: str, question: str, history: list[tuple[str,str]], db: Session) -> str:
    # extract video_id
    video_id: str = extract_video_id(video_url)
    # create chat session
    session: ChatSession = create_chat_session()
    # if not video_id exists in vectordb
    if not check_if_vectors_exist(video_id, session.vectorstore):
        # retrieve transcript
        documents: list[Document] = get_transcript(video_url=video_url, db=db)
        # chunk transcript
        chunks: list[Document] = chunk_documents(documents, chunk_size= 800, chunk_overlap= 50)
        # embed chunks, upload to vectordb
        embed_and_save(chunks)
    
    answer: str = session.ask(question=question, history = history, video_id=video_id)
    return answer