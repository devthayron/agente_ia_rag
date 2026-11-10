EMBEDDING_MODEL = "bge-m3:latest"
LLM_MODEL = "llama3.2:latest"
REASONING = False

# LLM_TEMPERATURE = 0
# LLM_MAX_TOKENS = 500

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RETRIEVER_K = 4

DEFAULT_PDF = "data/politica_rh.pdf"

SYSTEM_PROMPT = """Você é um assistente que responde perguntas sobre políticas internas com base nos documentos.
Use APENAS as informações do contexto abaixo para responder.
Se não encontrar a resposta, diga claramente que não sabe responder.
Responda em português do Brasil, de forma clara e objetiva.

Contexto: {context}

Pergunta: {question}

Resposta:"""
