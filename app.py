import os
import tempfile
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from agent import config
from agent.rag import build_chain_from_pdf

load_dotenv()

DEFAULT_PDF_PATH = Path(__file__).parent / config.DEFAULT_PDF
DEFAULT_DOC_ID = DEFAULT_PDF_PATH.name

OPCAO_PADRAO = f"Demonstração: {DEFAULT_DOC_ID}"
OPCAO_UPLOAD = "Enviar meu próprio PDF"

# Sugestões só aparecem para o documento demo, cujo conteúdo é conhecido.
SUGESTOES = {
    DEFAULT_DOC_ID: [
        "Quais são as regras de férias?",
        "Como funciona o processo de admissão?",
        "Como funciona o processo de desligamento?",
        "Quais benefícios a empresa oferece?",
    ],
}

st.set_page_config(page_title="Assistente RAG Local", layout="wide")


@st.cache_resource(show_spinner="Indexando documento...")
def get_chain_from_path(pdf_path: str):
    return build_chain_from_pdf(pdf_path)


@st.cache_resource(show_spinner="Indexando documento enviado...")
def get_chain_from_upload(file_bytes: bytes):
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        return build_chain_from_pdf(tmp_path)

    finally:
        os.unlink(tmp_path)


def initialize_chat():
    if "messages" not in st.session_state:
        st.session_state["messages"] = []


def reset_if_document_changed(doc_id):
    if st.session_state.get("doc_atual") != doc_id:
        st.session_state["messages"] = []
        st.session_state.pop("suggested_prompt", None)
        st.session_state["doc_atual"] = doc_id


def display_suggestions(doc_id):
    perguntas = SUGESTOES.get(doc_id, [])
    if not perguntas:
        return

    st.markdown("#### Exemplos de perguntas")

    col1, col2 = st.columns(2)

    for i, pergunta in enumerate(perguntas):
        coluna = col1 if i % 2 == 0 else col2

        with coluna:
            if st.button(pergunta, use_container_width=True):
                st.session_state["suggested_prompt"] = pergunta
                st.rerun()


def sidebar():
    chain = None
    doc_id = None

    with st.sidebar:
        st.title("Documento")

        opcao = st.radio(
            "Escolha a fonte:",
            [OPCAO_PADRAO, OPCAO_UPLOAD],
            label_visibility="collapsed",
        )

        try:
            if opcao == OPCAO_UPLOAD:
                arquivo = st.file_uploader("Selecione um arquivo PDF", type=["pdf"])
                if arquivo is not None:
                    doc_id = f"upload:{arquivo.name}"
                    chain = get_chain_from_upload(arquivo.getvalue())
            else:
                doc_id = DEFAULT_DOC_ID
                chain = get_chain_from_path(str(DEFAULT_PDF_PATH))

        except Exception as e:
            st.error(
                "Não foi possível indexar o documento. "
                "Verifique se o Ollama está rodando e se os modelos foram baixados.\n\n"
                f"Detalhe: {e}"
            )
            chain = None

        if st.button("Limpar chat", use_container_width=True):
            st.session_state["messages"] = []
            st.rerun()

    return chain, doc_id


def display_messages():
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])


def handle_chat(chain):
    prompt = st.chat_input("Pergunte sobre o documento selecionado...")

    if "suggested_prompt" in st.session_state:
        prompt = st.session_state.pop("suggested_prompt")

    if not prompt:
        return

    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"), st.spinner("Buscando informações..."):
        try:
            answer = chain.invoke(prompt)

        except Exception:
            answer = (
                "Erro ao gerar a resposta. "
                "Verifique se o Ollama está rodando (`ollama serve`)."
            )
        st.write(answer)

    st.session_state["messages"].append({"role": "assistant", "content": answer})


def main():
    initialize_chat()

    st.title("Assistente RAG Local")

    st.caption(
        "Processamento de IA local, sem APIs externas. "
        "Cada pergunta é respondida de forma independente, sem memória da conversa."
    )

    chain, doc_id = sidebar()
    reset_if_document_changed(doc_id)

    if chain is None:
        st.info("Envie um documento PDF na barra lateral para começar.")
        st.stop()

    display_messages()
    handle_chat(chain)

    if not st.session_state["messages"]:
        display_suggestions(doc_id)


if __name__ == "__main__":
    main()
