import pypdf
import streamlit as st
from langchain.document_loaders import PyPDFDirectoryLoader
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone
from langchain.llms import OpenAI


#uploaded_file = st.file_uploader("Upload your PDF")

arquivos_de_texto = PyPDFDirectoryLoader('./recursos/')
documentos = arquivos_de_texto.load()
#st.write(type(documentos))

for doc in documentos:
    doc.page_content.replace('\n', ' ')


embeddings = OpenAIEmbeddings()

## CONECTANDO COM A BASE DE DADOS PINECONE - USE A SUA CONTA E SUA PRÓPRIA API-KEY


pinecone.init(api_key=st.secrets["API_PINECONE"],
              environment="gcp-starter")

pine = Pinecone.from_documents(documentos, embeddings, index_name = "vector-database")

prompt_do_usuário = st.chat_input("Digite alguma coisa", key='chat_input')

#prompt_do_usuário = 'Fale sobre Ayrton'

if prompt_do_usuário:

    with st.chat_message("user"):
            st.markdown(prompt_do_usuário)

    busca = pine.similarity_search(prompt_do_usuário, k = 3)


    b0 = busca[0].page_content.replace('\n', ' ')
    b1 = busca[1].page_content.replace('\n', ' ')
    b2 = busca[2].page_content.replace('\n', ' ')


    prompt_final = f"""
    Escreva sempre em tom positivo e extrovertido.
    Elabore bem as respostas mas não fuja do tema da pergunta do usuário.

    Responda a pergunta do usúario considerando o conhecimento a seguir.

    {b0}

    {b1}

    ---

    A pergunta do usuário é: {prompt_do_usuário}

    """

    llm = OpenAI()
    resposta = llm(prompt_final)
    with st.chat_message("system"):
                st.markdown(resposta)
    #st.write(saida)