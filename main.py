from agent.ollama_client import OllamaClient

client = OllamaClient()

while True:
    msg = input("Digite sua mensagem (digite 'sair' para encerrar): ")

    if msg.lower() == "sair":
        break

    response = client.chat(msg)
    print(response)
    print("\n")
