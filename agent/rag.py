from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from agent import config


def load_pdf(pdf_path):
    return PyPDFLoader(pdf_path).load()


def split_into_blocks(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    return splitter.split_documents(documents)


def create_vectorstore(blocks):
    embeddings = OllamaEmbeddings(model=config.EMBEDDING_MODEL)
    return FAISS.from_documents(blocks, embeddings)


def create_chain(vectorstore):
    prompt = ChatPromptTemplate.from_messages([("system", config.SYSTEM_PROMPT)])
    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": config.RETRIEVER_K}
    )
    llm = ChatOllama(
        model=config.LLM_MODEL,
        reasoning=config.REASONING,
    )
    return (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )


def build_chain_from_pdf(pdf_path):
    """Pipeline completo: PDF -> chunks -> vectorstore -> chain."""
    documents = load_pdf(pdf_path)
    blocks = split_into_blocks(documents)
    vectorstore = create_vectorstore(blocks)
    return create_chain(vectorstore)
