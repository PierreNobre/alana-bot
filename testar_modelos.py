import openai
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

# Definir a chave de API
openai.api_key = os.getenv("OPENAI_API_KEY")

# Listar modelos disponíveis
try:
    models = openai.models.list()
    print("\n📌 Modelos disponíveis na sua conta:\n")
    
    for model in models:
        print(model.id)  # Corrigindo a forma de acessar os modelos

except Exception as e:
    print(f"❌ Erro ao buscar modelos: {e}")
