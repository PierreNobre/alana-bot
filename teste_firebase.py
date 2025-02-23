import firebase_admin
from firebase_admin import credentials, firestore

# Inicializar o Firebase com as credenciais
cred = credentials.Certificate("firebase_credentials.json")
firebase_admin.initialize_app(cred)

# Conectar ao Firestore
db = firestore.client()

# Teste: Criar um documento de teste no Firestore
doc_ref = db.collection("teste_conexao").document("teste1")
doc_ref.set({
    "mensagem": "Conexão com Firebase bem-sucedida!",
    "status": "ok"
})

print("✅ Conexão bem-sucedida! Verifique no Firebase Firestore.")
