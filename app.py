from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_groq import ChatGroq
from langchain_huggingface.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_huggingface.chat_models.huggingface import ChatHuggingFace
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Opções de provedores e modelos disponíveis
provedores = {
    'Groq': ['llama-3.3-70b-versatile', 'mixtral-8x7b'],
    'OpenAI': ['gpt-3.5-turbo-0125', 'gpt-4-turbo'],
    'Hugging Face': ['HuggingFaceH4/zephyr-7b-beta', 'mistralai/Mixtral-8x7B-Instruct-v0.1']
}

# Configuração da interface do Streamlit
st.title('Chatbot amigável')

# Sidebar para seleção do provedor e modelo
st.sidebar.header('Configuração do Modelo')
provedor_selecionado = st.sidebar.selectbox('Escolha o provedor:', list(provedores.keys()))

# Com base no provedor, exibir os modelos disponíveis
modelo_selecionado = st.sidebar.selectbox('Escolha o modelo:', provedores[provedor_selecionado])

# Inicializando o modelo com base na escolha do usuário
if provedor_selecionado == 'OpenAI':
    chat = ChatOpenAI(model=modelo_selecionado)
elif provedor_selecionado == 'Groq':
    chat = ChatGroq(model=modelo_selecionado)
elif provedor_selecionado == 'Hugging Face':
    llm = HuggingFaceEndpoint(repo_id=modelo_selecionado)
    chat = ChatHuggingFace(llm=llm)

# Inicializa o histórico de mensagens na sessão
if 'historico_chat' not in st.session_state:
    st.session_state.historico_chat = []
    st.session_state.historico_chat.append(SystemMessage(content='Você é um assistente amigável.'))

# Exibe o histórico do chat na interface
for mensagem in st.session_state.historico_chat:
    if isinstance(mensagem, AIMessage): # Mensagem do chatbot
        with st.chat_message('ai'):
            st.write(mensagem.content)
    if isinstance(mensagem, HumanMessage): # Mensagem do usuário
        with st.chat_message('human'):
            st.write(mensagem.content)

# Captura a entrada do usuário no chat
mensagem_usuario = st.chat_input('Digite sua mensagem aqui...')

# Processa a mensagem do usuário e gera uma resposta do chatbot
if mensagem_usuario:
    # Exibe a mensagem do usuário na interface do chat
    with st.chat_message('human'):
        st.write(mensagem_usuario)

    # Adiciona a mensagem do usuário ao histórico
    st.session_state.historico_chat.append(HumanMessage(content=mensagem_usuario))

    # Exibe um espaço temporário para a resposta do assistente
    with st.chat_message('ai'):
        espaco = st.empty() # Placeholder para atualização dinâmica
        espaco.write('Pensando...')

        # Obtém a resposta do modelo com base no histórico da conversa
        resposta = chat.stream(st.session_state.historico_chat)

        # Inicializa uma string para armazenar a resposta completa do chatbot
        resposta_completa = ''

        # Exibe a resposta em tempo real conforme ela é gerada
        for trecho in resposta:
            resposta_completa += trecho.content # Acumula o texto gerado
            espaco.write(resposta_completa) # Atualiza a interface dinamicamente

    # Adiciona a resposta do modelo ao histórico da conversa
    st.session_state.historico_chat.append(AIMessage(content=resposta_completa))
