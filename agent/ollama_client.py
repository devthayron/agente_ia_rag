import requests

from agent.system_prompt import SYSTEM_PROMPT


class OllamaClient:
    def __init__(self, model="Qwen3:latest", history=SYSTEM_PROMPT):
        self.url = "http://localhost:11434/api/chat"
        self.model = model
        self.history = history if history is not None else []

    def chat(self, mensagem):

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": mensagem}],
                "stream": False,
            },
            timeout=120,
        )

        # debug: imprime a resposta completa da API
        # data = response.json()
        # print(json.dumps(data, indent=4, ensure_ascii=False))

        response.raise_for_status()

        # adiciona a mensagem do usuário e a resposta do assistente ao histórico de mensagens
        self.history.append({"role": "user", "content": mensagem})
        self.history.append(
            {"role": "assistant", "content": response.json()["message"]["content"]}
        )

        return response.json()["message"]["content"]
