from app.services.embedding import get_embedding_function
from langchain_ollama import OllamaLLM
from langchain.vectorstores import VectorStore
import logging

logger = logging.getLogger(__name__)

class ChatMemory:
    def __init__(self, max_turns=5):
        self.max_turns = max_turns
        self.buffer = [] # list of (user, assistant) tuples

    def append(self, user_message: str, assistant_message: str):
        self.buffer.append((user_message, assistant_message))
        logger.debug(f"Appended (user_message, assistant_message) tumple to memory")

        if len(self.buffer) > self.max_turns:
            self.buffer.pop(0)
            logger.debug("Memory buffer capacity exceeded {self.max_turns}, removed oldest message")

    def to_prompt(self):
        history = [f"User: {u}; \nAssistant: {a}" for u, a in self.buffer]
        logger.debug(f"ChatMemory.to_prompt called. History: {history}")
        return "\n\n".join(history)

class TranscriptReceiver:
    def __init__(self, vector_store: VectorStore, embedding_fn, k=4):
        self.retriever = vector_store.as_retriever(
            search_kwargs={"k":k}
        )
        logger.info(f"Initialised TranscriptReciever with vector store {vector_store.__repr__}, {k} retrival context chunks")

    def get_context(self, query: str) -> str:
        results = self.retriever.similarity_search_with_relevance_scores(query=query)
        context = "\n\n".join(result[0].page_content for result in results)
        logger.debug(f"TranscriptReciever.get_context called. Context: {context}")

        return context
        
class ChatSession:
    def __init__(self, llm, retriever: TranscriptReceiver, memory: ChatMemory):
        self.llm = llm
        self.retriever = retriever
        self.memory = memory
        logger.debug(f"ChatSession initialised with {llm.__str__}, retriever {retriever.__str__}, memory {memory.__str__}")

    def ask(self, question: str) -> str:
        # 1) Retrieve context
        context = self.retriever.get_context(query = question)

        # 2) Build the prompt
        prompt_blocks = []
        
        history = self.memory.to_prompt()
        if history:
            prompt_blocks.append(history)

        prompt_blocks.append("Relevant context: \n\n" + context)

        prompt_blocks.append(f"User: {question} \n\n Assistant:")

        prompt = "\n".join(prompt_blocks)
        logger.debug("Prompt: {prompt}")

        # 3) Call your LLM
        answer = self.llm.generate(prompt)
        logger.info("LLM called. Answer: {answer}")

        # 4) Update memory
        self.memory.append((question, answer))