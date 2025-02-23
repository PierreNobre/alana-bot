from crewai import Agent, Task, Crew
import openai

# 🔹 Configure sua chave da OpenAI
openai.api_key = "SUA_OPENAI_API_KEY"

# 🔹 Defina o ID da Agente Alana no Assistants API
ASSISTANT_ID = "asst_FCkLAkaa1nF150w3vEnc8ywv"  # Use seu Assistant ID

# 🔹 Criando a Agente Alana com base no Assistants API
class OpenAIAssistantAgent:
    def __init__(self, assistant_id):
        self.assistant_id = assistant_id

    def execute_task(self, input_text):
        response = openai.beta.threads.create_and_run(
            assistant_id=self.assistant_id,
            messages=[{"role": "user", "content": input_text}]
        )
        return response["choices"][0]["message"]["content"]

alana = Agent(
    role="Assistente Virtual de Vendas",
    goal="Realizar pré-atendimento e qualificação de leads para a Galeria Nobre Imobiliária usando a Agente do GPT Assistants API.",
    backstory="Você é Alana, uma assistente virtual da Galeria Nobre Imobiliária. Sua função é atender leads conforme os scripts definidos.",
    allow_delegation=False,
    verbose=True,
    custom_llm=OpenAIAssistantAgent(ASSISTANT_ID)  # Conectando à Agente do OpenAI Assistants API
)

tarefa_atendimento = Task(
    description="Responder perguntas sobre imóveis conforme os scripts da Agente Alana no Assistants API.",
    agent=alana,
    expected_output="Mensagem personalizada seguindo o script configurado no Assistants API."
)

equipe = Crew(
    agents=[alana],
    tasks=[tarefa_atendimento]
)

if __name__ == "__main__":
    equipe.kickoff()
