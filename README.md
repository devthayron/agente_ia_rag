# Assistente RAG Local

Assistente de IA interno e local que responde perguntas com base nos documentos da empresa. Sem custo de API e sem enviar dados para fora.

1. O PDF é carregado e dividido em trechos (chunks).
2. Cada trecho vira um vetor (embedding) e é indexado no FAISS.
3. A pergunta busca os trechos mais parecidos.
4. O LLM local responde usando só esses trechos como contexto.

## Stack

- Python 3.10+
- Streamlit (interface)
- LangChain + langchain-ollama
- FAISS (busca vetorial)
- pypdf (leitura de PDF)
- Ollama (execução dos modelos locais)

## Pré-requisitos

### 1. Instalar o Ollama

Baixe pelo link oficial: **https://ollama.com/download**

- Windows: baixe e execute o instalador `.exe`
- macOS: baixe o `.dmg` e arraste para Aplicativos
- Linux:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Confirme a instalação:

```bash
ollama --version
```

### 2. Baixar os dois modelos de IA local

O projeto usa **dois modelos**: um de linguagem (gera a resposta) e um de embeddings (indexa e busca nos PDFs).

```bash
# Modelo de linguagem (LLM)
ollama pull llama3.2

# Modelo de embeddings
ollama pull nomic-embed-text
```

Páginas dos modelos:

- https://ollama.com/library/llama3.2
- https://ollama.com/library/nomic-embed-text

> Nota: modelos leves, feitos para PCs comuns. Para usar outro conforme seu hardware, rode `ollama pull <modelo>` e altere o nome em `agent/config.py`

Verifique se baixaram:

```bash
ollama list
```

> **Importante:** os nomes acima precisam ser idênticos aos configurados em `agent/config.py`. Se você usa outros modelos lá, faça `ollama pull <nome-do-modelo>` para cada um.

Se o Ollama não estiver rodando em segundo plano, inicie com:

```bash
ollama serve
```

## Instalação do projeto

```bash
# Clonar o repositório
git clone "https://github.com/devthayron/agente-ia-rag.git"
cd agente-ia-rag

# Criar e ativar o ambiente virtual
python3 -m venv venv

# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

## Executando

```bash
streamlit run app.py
```

Abra http://localhost:8501 no navegador.

- Sem upload: usa o documento padrão `politica_rh.pdf`.
- Com upload: indexa o PDF enviado e responde com base nele.

## Estrutura do projeto

```
.
├── app.py                  # Interface Streamlit
├── agent/
│   ├── config.py           # Config do agente
│   └── rag.py              # Pipeline RAG 
├── data/
│   └── politica_rh.pdf
│   
├── requirements.txt
└── README.md
```

## Problemas comuns

| Problema                              | Causa provável                 | Solução                                  |
| ------------------------------------- | ------------------------------- | ------------------------------------------ |
| `Connection refused` na porta 11434 | Ollama não está rodando       | Execute `ollama serve`                   |
| `model not found`                   | Modelo não baixado             | Execute `ollama pull <modelo>`           |
| Respostas lentas                      | Modelo grande para sua máquina | Use um modelo menor (ex.: `llama3.2:1b`) |
| PDF escaneado sem resposta            | PDF é imagem, sem texto        | Faça OCR antes de enviar                  |

## Autor

**Thayron Higlânder**

LinkedIn: [https://www.linkedin.com/in/thayron-higlander](https://www.linkedin.com/in/thayron-higlander)

## Licença

Este projeto está sob a licença [MIT](LICENSE).
