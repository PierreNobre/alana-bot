from flask import Flask, request, Response
from google.cloud import firestore
from twilio.twiml.messaging_response import MessagingResponse
import datetime
import os
from openai import OpenAI

# Inicializar Firebase Firestore
db = firestore.Client()

# Inicializar OpenAI Client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/webhook", methods=["POST", "GET"])
def webhook():
    if request.method == "GET":
        return "Webhook está ativo!", 200

    data = request.form
    numero_cliente = data.get("From").replace("whatsapp:", "").strip()
    mensagem_recebida = data.get("Body").strip()

    print(f"Mensagem recebida de {numero_cliente}: {mensagem_recebida}")

    # Referência ao documento do cliente no Firestore
    doc_ref = db.collection("conversas").document(numero_cliente)
    doc = doc_ref.get()

    # Recuperar histórico de mensagens
    historico = []
    if doc.exists:
        historico = doc.to_dict().get("historico", [])

    # Criar um contexto útil para a Agente Alana
    contexto = "\n".join(
        [f"{msg['remetente']}: {msg['mensagem']}" for msg in historico[-5:]]
    )

    # Construir um prompt mais inteligente para o Assistants API
    prompt_completo = f"""
    Histórico da conversa:
    {contexto}

    O cliente enviou a seguinte mensagem agora:
    Cliente: {mensagem_recebida}

    Responda de maneira objetiva e coerente, seguindo as diretrizes do atendimento.
    """

    # Enviar a mensagem para a Assistente Alana no Assistants API
    resposta_ia = chamar_assistant_api(prompt_completo)

    # Adicionar nova mensagem ao histórico
    historico.append({
        "mensagem": mensagem_recebida,
        "remetente": "cliente",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
    })

    # Adicionar resposta da Alana ao histórico
    historico.append({
        "mensagem": resposta_ia,
        "remetente": "Alana",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
    })

    # Atualizar Firestore com o novo histórico
    doc_ref.set({
        "historico": historico,
        "ultima_interacao": datetime.datetime.now(datetime.UTC).isoformat()
    })

    # Criar resposta para o WhatsApp
    twilio_response = MessagingResponse()
    twilio_response.message(resposta_ia)

    return Response(str(twilio_response), status=200, mimetype="application/xml")


def chamar_assistant_api(prompt):
    """
    Função para chamar a Assistants API da OpenAI e obter uma resposta baseada no histórico e na nova mensagem.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Você é Alana, a assistente da Galeria Nobre Imobiliária. Responda de forma objetiva e natural."},
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
