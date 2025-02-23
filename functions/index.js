const functions = require("firebase-functions");
const admin = require("firebase-admin");
const express = require("express");
const cors = require("cors");
const axios = require("axios");

// Inicializa o Firebase Admin
admin.initializeApp();
const db = admin.firestore();

// Configuração do Express para o Webhook
const app = express();
app.use(cors({ origin: true }));
app.use(express.json());

// Webhook do WhatsApp
app.post("/webhook", async (req, res) => {
    try {
        const { From, Body } = req.body;

        if (!From || !Body) {
            return res.status(400).send("Requisição inválida");
        }

        // Formatar número de telefone
        const numeroCliente = From.replace("whatsapp:", "");

        // Recuperar histórico do Firebase Firestore
        const docRef = db.collection("conversas").doc(numeroCliente);
        const doc = await docRef.get();
        let historico = doc.exists ? doc.data().historico : [];

        // Adicionar nova mensagem ao histórico
        historico.push({ mensagem: Body, remetente: "cliente", timestamp: new Date().toISOString() });

        // Criar o prompt para a IA
        const prompt = `Histórico recente: ${JSON.stringify(historico.slice(-5))}
        Cliente: ${Body}
        Alana deve responder conforme o script pré-definido da imobiliária.`;

        // Chamar API da OpenAI
        const resposta = await axios.post(
            "https://api.openai.com/v1/chat/completions",
            {
                model: "gpt-4-turbo",
                messages: [{ role: "system", content: "Você é a assistente Alana." }, { role: "user", content: prompt }],
                max_tokens: 100,
            },
            {
                headers: { Authorization: `Bearer ${functions.config().openai.key}` },
            }
        );

        const respostaAlana = resposta.data.choices[0].message.content;

        // Adicionar resposta ao histórico
        historico.push({ mensagem: respostaAlana, remetente: "Alana", timestamp: new Date().toISOString() });

        // Atualizar Firestore
        await docRef.set({ historico, numero_cliente: numeroCliente, ultima_interacao: new Date() }, { merge: true });

        // Responder ao WhatsApp
        res.status(200).send(respostaAlana);
    } catch (error) {
        console.error("Erro no Webhook:", error);
        res.status(500).send("Erro interno no servidor");
    }
});

// Exportar a função para o Firebase
exports.api = functions.https.onRequest(app);
