import tempfile

import streamlit as st
from dotenv import load_dotenv

from agent import config
from agent.rag import build_chain_from_pdf

load_dotenv()


@st.cache_resource(show_spinner="Indexando documento padrão...")
def get_chain_default():
    return build_chain_from_pdf(config.DEFAULT_PDF)


@st.cache_resource(show_spinner="Indexando documento...")
def get_chain_from_upload(file_bytes: bytes):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name
    return build_chain_from_pdf(tmp_path)


st.title("Assistente RAG — Políticas Internas")

arquivo = st.file_uploader("Selecione um PDF (opcional)", type=["pdf"])

if arquivo:
    chain = get_chain_from_upload(arquivo.getvalue())
    st.success(f"Usando: {arquivo.name}")
else:
    chain = get_chain_default()
    st.info("Usando o documento fictício padrão: politica_rh.pdf")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

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
