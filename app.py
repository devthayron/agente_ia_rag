import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


def load_pdf(pdf_path="data/politica_rh.pdf"):  # ler o pdf e extrair o texto do pdf
    pdf_loader = PyPDFLoader(pdf_path)
    text = pdf_loader.load()
    return text


text_pdf = load_pdf()


def split_into_blocks(text_pdf):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    block_list = splitter.split_documents(text_pdf)
    return block_list


block_list = split_into_blocks(text_pdf)
# print(len(block_list))
# print(block_list[0])
# print(block_list[1])


def create_vectorstore(block_list):
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.from_documents(block_list, embeddings)
    return vectorstore


vectorstore = create_vectorstore(block_list)


def create_chain():

    prompt_template = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                """Você é um assistente geral que responde perguntas sobre políticas internas com base nos documentos.
    Use APENAS as informações do contexto abaixo para responder.
    Se não encontrar a resposta, diga claramente que não sabe responder.
    Responda em português do Brasil, de forma clara e objetiva.

    Contexto: {context}

    A pergunta: {question}

    Resposta:""",
            )
        ]
    )

    retriever = vectorstore.as_retriever(
        search_type="similarity", search_kwargs={"k": 4}
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        max_tokens=500,
    )

    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt_template
        | llm
        | StrOutputParser()
    )

    return chain


chain = create_chain()

# interface do chat
st.title("Assistente RAG — Políticas Internas")

arquivo = st.file_uploader("Selecione um arquivo", type=["pdf"])

if arquivo:
    st.success(f"Arquivo recebido: {arquivo.name}")

# inicia a lista de mensagens
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# exibe as mensagens na tela
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

prompt = st.chat_input("Pergunte sobre as políticas da empresa...")
if prompt:
    st.session_state["messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"), st.spinner("Buscando..."):
        answer = chain.invoke(prompt)
        st.write(answer)

    st.session_state["messages"].append({"role": "assistant", "content": answer})
