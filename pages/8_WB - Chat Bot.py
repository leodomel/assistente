from datetime import datetime
import streamlit as st
import pandas as pd

from langchain.chains import LLMChain, OpenAIModerationChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import openai
from openai import OpenAI

from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.callbacks import get_openai_callback

import pdfkit

from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
import matplotlib.pyplot as plt

import os
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]


#moderation_chain_error = OpenAIModerationChain()

#moderation_chain_error.run("This is okay")
if "estilo_ant" not in st.session_state:
    st.session_state.estilo_ant = None

if "estilo_atual" not in st.session_state:
    st.session_state.estilo_atual = None

if "desabilita_input" not in st.session_state:
    st.session_state.desabilita_input = False

if "finaliza" not in st.session_state:
    st.session_state.finaliza = False

def update_estilo_session():
    st.session_state.estilo_ant = st.session_state.estilo_atual
    st.session_state.estilo_atual= st.session_state.estilo
    return


def chat_moderations(texto):
    client = OpenAI()
    response = dict(client.moderations.create(input=texto).results[0])
    return response['flagged']

def get_tokens_response(api, texto):
  with get_openai_callback() as cb:
    result = api.invoke(texto)
    return cb.total_tokens, cb.total_cost

def monta_registro_chat(conversa, tokens, custo, pergunta, resposta):
    registro = {
            "Data e Hora": [datetime.now().strftime('%d-%m-%Y %H:%M:%S')],
            "Tokens": [tokens],
            "Custo": [custo],
            "Diálogo": ["user: " + pergunta + " \n system: " + resposta]
        }

    return conversa.append(registro, ignore_index=True)

#def gera_pdf(df):
#  plt.figure(figsize=(8, 4))
#  plt.axis('off')
#
#  # Criando a tabela a partir do DataFrame
#  tabela = plt.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')
#
#  # Estilizando a tabela
#  tabela.auto_set_font_size(False)
#  tabela.set_fontsize(10)
#  tabela.scale(1.2, 1.2)
#
#  # Salvando a tabela como um arquivo PDF
#  return type(plt.savefig('tabela_dataframe.pdf', bbox_inches='tight', pad_inches=0.5))

def gera_pdf(dataset, c, t):
  env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
  template = env.get_template("template.html")
  tabela_html = dataset.to_html()
  str_html = '<br><p>A quantidade total de Tokens do diálogo é ' + str(t) + ' , tendo o Custo total de ' + str(c) + '</p>'
  #st.write(tabela_html + str_html)
  tabela_html = tabela_html + str_html
  html = template.render(tabela_html=tabela_html)
  return pdfkit.from_string(html, False)

def finaliza_dialogo():
    if "finaliza" not in st.session_state:
        st.session_state.finaliza = False
    else:
        st.session_state.finaliza = st.session_state.chk_finalizar

#flai = 'recursos/logo flai com sombra.png'

temperatura = 1
token = None

if "mdf" not in st.session_state:
    st.session_state.mdf = pd.DataFrame(columns=['Data e Hora','Tokens','Custo','Diálogo'])

#st.chat_message(name = 'user', avatar ='C:/Milena/Pós SENAICIMATEC/Machine Learning Hands on/Assistente/recursos/1.png')

# Iniciar Historico Chat

st.markdown('---')

abas = ['💙 Chat', '🧡 Parâmetros', '❤ Histórico']

aba1, aba2, aba3 = st.tabs(abas)


prompt = st.chat_input("Digite alguma coisa", key='chat_input')

with aba1:

    st.title("WB - Assistente de Violência contra a Mulher")
    c0, c1, _, _, _, _, _, _, _, _, _, _= st.columns([0.5,1.2,1,1,1,1,1,1,1,1,1,1])

    with c0:
        c = st.checkbox(label = 'Finalizar', 
            help='Configura os prediotres marcados na seleção múltipla como nulo', 
            on_change=finaliza_dialogo,
            disabled=False, 
            key='chk_finalizar',
            label_visibility="collapsed") #hidden #collapsed
    with c1:
        st.write("Finalizar")

    chat = ChatOpenAI(temperature=round(temperatura, 1), max_tokens=token, model_name="gpt-3.5-turbo")

    if "mensagens" not in st.session_state:
    #st.session_state.mensagens = [{"role": 'system', "content": 'Você será uma assistente jurídico sobre a lei Maria da Penha brasileira e violência contra a mulher. Sua função é será um orientador para mulheres que sofrem algum tipo de violência para dar conselhos baseado na lei, jurispridência brasileira e casos tratados pelo Ministério Público da Bahia. Se apresente na primeira mensagem.'}]

        st.session_state.mensagens = [ SystemMessage(
            content="Você será uma assistente jurídico sobre a lei Maria da Penha brasileira e violência contra a mulher. Sua função é será um orientador para mulheres que sofrem algum tipo de violência para dar conselhos baseado na lei, jurispridência brasileira e casos tratados pelo Ministério Público da Bahia. Use sempre uma linguagem positiva, acolhedora e gentil!'"
        )]

    # Aparecer o Historico do Chat na tela
    for mensagens in st.session_state.mensagens[1:]:

        with st.chat_message('system' if isinstance(mensagens, SystemMessage) else 'user'):
            st.markdown(mensagens.content)


    # React to user input
    

    if prompt:
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)

        if not(chat_moderations(prompt)):
        # Add user message to chat history
            st.session_state.mensagens.append(HumanMessage(
            content=prompt))


            chat = ChatOpenAI(temperature=round(temperatura, 1), max_tokens=token, model_name="gpt-3.5-turbo")
            chamada = chat(st.session_state.mensagens)

            resposta = chamada.content

        # Display assistant response in chat message container
            with st.chat_message("system"):
                st.markdown(resposta)
        # Add assistant response to chat history
            st.session_state.mensagens.append(SystemMessage(
            content=resposta))

            t, c = get_tokens_response(chat, st.session_state.mensagens)

            st.session_state.mdf = monta_registro_chat(st.session_state.mdf, t, c, prompt, resposta)
            #st.write(st.session_state.mdf) 

        else:
            with st.chat_message("system"):
                st.markdown('Pergunta viola a política de conteúdo da OpenAI, favor reformular sua pergunta')   


with aba2:
    
    del st.session_state.chat_input
    st.divider()
    st.subheader('Parâmetros para a resposta')

    col1, col2, col3 = st.columns(3)

    with col1:
        #st.subheader('Controle de Criatividade')
        temperatura = st.number_input(label = 'Criatividade', 
            min_value = 0., 
            max_value = 2.0, 
            value = 1., 
            step = 0.1, 
            format = "%.1f", # '%d' para inteiros, '%e' para notacao cientifica, '%f' para numeros reais
            key = None, 
            help = 'Defina o nível de criatividade na resposta', 
            on_change = None, 
            args = None, 
            kwargs = None, 
            disabled = False, 
            label_visibility = "visible")

    #st.write(round(temperatura, 1)) 


    with col2:
        token = st.number_input(label = 'Limite de tokens', 
            min_value = 10, 
            max_value = None, 
            value = 2000, 
            step = 1, 
            format = "%d", # '%d' para inteiros, '%e' para notacao cientifica, '%f' para numeros reais
            key = None, 
            help = 'Defina o número máximo de tokens para a resposta', 
            on_change = None, 
            args = None, 
            kwargs = None, 
            disabled = False, 
            label_visibility = "visible")

    st.divider()

    with col3:
        estilo = st.selectbox(label = 'Estilo', 
            options = ['minimalista', 'objetivo', 'amigável', 'não amigável', 'simplista', 'elaborado', 'jocoso'] ,
            index = None, 
            key = 'estilo', 
            help = 'Estilo da resposta', 
            on_change = update_estilo_session, 
            args=None, 
            kwargs=None,
            disabled = False, 
            label_visibility = "visible")


        if not(estilo == None) and (st.session_state.estilo_ant != st.session_state.estilo_atual): 
            chat = ChatOpenAI(temperature=round(temperatura, 1), max_tokens=token, model_name="gpt-3.5-turbo")
            chat([SystemMessage(content='Altere o estilo das respostas. Utilize uma liguagem' + str(estilo) + 'nas respostas')])



with aba3:
    st.header('Histórico')
    st.dataframe(st.session_state.mdf, use_container_width=True)
   
    if (len(st.session_state.mdf) > 0) and st.session_state.finaliza:
        c = st.session_state.mdf.loc[:,'Custo'].sum()
        t = st.session_state.mdf.loc[:,'Tokens'].sum()

        st.download_button(
            "⬇️ Download PDF",
            data=gera_pdf(st.session_state.mdf, c, t),
            file_name="hist_dialogo.pdf",
            mime="application/octet-stream")
