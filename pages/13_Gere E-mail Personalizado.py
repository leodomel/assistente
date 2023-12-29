import streamlit as st 

st.header('💙 Geração de E-mail Personalizado')

import pandas as pd
from langchain.llms import OpenAI
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

import pdfkit

from jinja2 import Environment, PackageLoader, select_autoescape, FileSystemLoader
import html


def dataframe_with_selections(df, nome):
    df_with_selections = df.copy()
    df_with_selections.insert(0, "Select", False)

    # Get dataframe row-selections from user with st.data_editor
    edited_df = st.data_editor(
        df_with_selections,
        hide_index=True,
        column_config={"Select": st.column_config.CheckboxColumn(required=True)},
        disabled=df.columns,
        key=nome,
    )

    # Filter the dataframe using the temporary column, then drop the column
    selected_rows = edited_df[edited_df.Select]
    return selected_rows.drop('Select', axis=1)
def get_options():
    return {
        'encoding': 'UTF-8',
        'enable-local-file-access': True
    }

def gera_pdf(dataset):
    import base64
    import os 
    # Path to wkhtmltopdf binary
    # wkhtmltopdf_path = os.path.join(os.getcwd(), 'wkhtmltopdf', 'bin', 'wkhtmltopdf')
    # if not os.path.isfile(wkhtmltopdf_path):
    #     raise FileNotFoundError("wkhtmltopdf executable not found at %s" % wkhtmltopdf_path)
    # # Configure pdfkit to use the binary
    # config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)


    env = Environment(loader=FileSystemLoader("."), autoescape=select_autoescape())
    template = env.get_template("template_email.html")
    tabela_html = dataset.to_html()
    html = template.render(tabela_html=tabela_html)
    config = pdfkit.configuration(wkhtmltopdf='/opt/bin/wkhtmltopdf')
    # pdfkit.from_string(html, 'output.pdf', configuration=config)
    return pdfkit.from_string(html, False, verbose=True, configuration=config)
    # import weasyprint
    # out_pdf = '/tmp/demo.pdf'
    # return weasyprint.HTML(html).write_pdf(out_pdf)

dados = pd.read_csv('recursos/PesquisaResumida.csv')

dados['E-mail Personalizado'] = ''

orientacao = "Você será um vendedor de cursos de Inteligência Artificial, Machine Learning, Data Science.\
    Sua função será gerar um e-mail personalizado com as caracteristicas fornecidas do cliente para convencê-lo de fazer o curso\
    Seja sutil na persuação para que o cliente compre o curso e utilize uma linguagem objetiva e clara\
    Os dados dos clientes serão passados baseados nas seguintes perguntas\
    Nome completo:\
    Qual a sua idade?\
    Sexo\
    Nível de Escolaridade\
    Qual sua graduação?\
    Qual desses são seus objetivos alinhados a Data Science?\
    Quais áreas você tem interesse em ver aplicações?\
    O que você considera ser sua maior dificuldade para se tornar um Cientista de Dados?\
    Quais as 3 perguntas sobre Data Science que você me faria se tivesse a oportunidade de conversar comigo? "

selection_01 = dataframe_with_selections(dados, 'antes')

st.divider()

_, c1, _ = st.columns([1,3,1])


with c1:
	botao = st.button('Gerar E-mails',
		type = 'primary',
		use_container_width = True)


if botao:

	for indice, linha in selection_01.iterrows():
		mensagem = []
		mensagem = [SystemMessage(content=orientacao)]
		mensagem.append(HumanMessage(content=str(linha.to_dict())))
		#st.write(mensagem)
		chat = ChatOpenAI(temperature=1, model_name="gpt-3.5-turbo")
		email = chat(mensagem)
		#st.write(email)
		selection_01.loc[indice, 'E-mail Personalizado'] = email.content



st.divider()

st.write("Cadastros Selecionados Para Geração de E-mail")
st.dataframe(selection_01, use_container_width=True)


st.divider()

#selection_02 = dataframe_with_selections(selection_01, 'depois')
#st.write("Cadastros Selecionados")
#st.write(selection_02)

imp = pd.DataFrame()

if (len(selection_01) > 0):
    for i, row in selection_01.iterrows():
        imp = imp.append(pd.DataFrame([{'Data': row['E-mail Personalizado']}], index=['0']), ignore_index=True)

    st.download_button(
        "⬇️ Download PDF E-mail",
        data=gera_pdf(imp),
        key='bt_email',
        file_name="Email_Personalizado.pdf",
        mime="application/octet-stream")
        
	