import streamlit as st 
import pandas as pd
import numpy as np
from pycaret.regression import load_model, predict_model
#from pycaret.datasets import get_data
#'position_grid', 'ct_points', 'ct_position', 'ct_wins', dr_wins', 'pt_stop', 'pt_dur_milliseconds'

dados = pd.read_csv('recursos/resul_races.csv')
modelo = load_model('recursos/modelo-previsao-se-piloto-pontuou')


if "multipla" not in st.session_state:
    st.session_state.multipla = []

dicionario = {
    'ct_points': 'Qt Pontos da Equipe',
    'ct_position': 'Posição da Equipe no Campeonato',
    'ct_wins': 'Qt Vitórias da Equipe',
    'dr_wins':'Qt Vitórias do Piloto',
    'pt_stop': 'Qt de Pit Stop na Corrida',
    'pt_dur_milliseconds': 'Duração média dos Pit Stops'
}

valores_nao_nulos ={
        'ct_points': 1, 
        'ct_position': 1, 
        'ct_wins': 1,
        'dr_wins':1, 
        'pt_stop':1, 
        'pt_dur_milliseconds':1}
        
#col0, col1, col2, col3, col4, col5 = st.columns([3,3,3,3,3,3])

#print(valores_nao_nulos)

def traduz_preditores(t_valor):
    chaves_correspondentes = [chave for chave, valor in dicionario.items() if valor == t_valor]
    #st.write(chaves_correspondentes)
    return chaves_correspondentes[0]

def rehabilita_preditores():
    valores_nao_nulos ={
        'ct_points': 1, 
        'ct_position': 1, 
        'ct_wins': 1,
        'dr_wins':1, 
        'pt_stop':1, 
        'pt_dur_milliseconds':1}
    return valores_nao_nulos

def load():
    aux = {'position_grid': position_grid,
            'dr_wins': [dr_wins if valores_nao_nulos['dr_wins'] else np.NaN],
            'pt_stop': [pt_stop if  valores_nao_nulos['pt_stop'] else np.NaN],
            'pt_dur_milliseconds': [pt_dur_milliseconds if  valores_nao_nulos['pt_dur_milliseconds'] else np.NaN],
            'ct_position': [ct_position if  valores_nao_nulos['ct_position'] else np.NaN],
            'ct_points': [ct_points if  valores_nao_nulos['ct_points'] else np.NaN],
            'ct_wins': [ct_wins if  valores_nao_nulos['ct_wins'] else np.NaN]}
    return aux

def desabilita_preditores():
    rehabilita_preditores()
    
    if(len(st.session_state.multipla) > 0):
        for selecao in st.session_state.multipla:
            valores_nao_nulos[traduz_preditores(selecao)] = 0 
    return 


st.header('Modelo de Previsão de Pontuação do Piloto')

st.divider()
st.write('Opcionalmente, selecione as caracteristicas que não possuem valor')

col0, col1= st.columns([0.5,3])

with col0:

     c = st.checkbox(label = 'Reseta entrada com nulo', 
        help='Configura os prediotres marcados na seleção múltipla como nulo', 
        on_change=desabilita_preditores,
        disabled=False, 
        label_visibility="collapsed") #hidden #collapsed

with col1:
            
        multipla = st.multiselect(label = 'Preditores Inexistentes', 
            options = list(dicionario.values()), #list(valores_nao_nulos.keys()), 
            key='multipla', 
            help = 'Selecione os preditores que deverão ser nulos, ao final marque o checkbox', 
            on_change=None, 
            args=None, 
            kwargs=None,
            disabled=False, 
            label_visibility="visible", 
            max_selections = 6)
            
st.divider()

st.write('Entre com as caracteristicas para fazer uma previsão se o piloto pontuou na corrida.')
st.write('\n')
    
col2, col3, col4 = st.columns([3,3,3])

with col2:

    position_grid = st.select_slider(label = 'Posição de Largada', 
        options = sorted(dados['position_grid'].unique()),
        key=None, 
        help='Entre com a posição de largada', 
        on_change=None, 
        args=None, 
        kwargs=None,
        disabled = 0, 
        label_visibility="visible")

    dr_wins = st.select_slider(label = 'Quantidade de vitórias do piloto', 
        options = sorted(dados['dr_wins'].unique()),
        key=None, 
        help='Entre com a quantidade de vitórias do piloto', 
        on_change=None, 
        args=None, 
        kwargs=None,
        disabled=False, 
        label_visibility="visible")


with col3:
        
    ct_points = st.slider(label = 'Quantidade de Pontos de Construtores', 
        min_value=min(dados['ct_points']), 
        max_value=max(dados['ct_points']), 
        value= 0.0, 
        step=0.1, 
        help='Quantidade de Pontos de Construtores')

    ct_position = st.select_slider(label = 'Posição da Equipe no campeonato', 
        options = sorted(dados['ct_position'].unique()),
        key=None, 
        help='Entre com Posição da Equipe no campeonato', 
        on_change=None, 
        args=None, 
        kwargs=None,
        #disabled=valores_nao_nulos['ct_position'], 
        label_visibility="visible")

    ct_wins = st.select_slider(label = 'Quantidade de vitórias da equipe', 
        options = sorted(dados['ct_wins'].unique()),
        key=None, 
        help='Entre com a quantidade de vitórias da equipe', 
        on_change=None, 
        args=None, 
        kwargs=None,
        disabled=False, 
        label_visibility="visible")
        
        
with col4:

    pt_stop = st.select_slider(label = 'Quantidade de Pit Stops', 
        options = sorted(dados['pt_stop'].unique()),
        key=None, 
        help='Entre com a quantidade de Pit Stops', 
        on_change=None, 
        args=None, 
        kwargs=None,
        disabled=False, 
        label_visibility="visible")

    pt_dur_milliseconds = st.number_input(label = 'Tempo médio dos Pit Stops', 
        min_value = 0.0, 
        value = dados['pt_dur_milliseconds'].mean(), 
        step = 0.1, 
        #format = "%.1f", # '%d' para inteiros, '%e' para notacao cientifica, '%f' para numeros reais
        key = None, 
        help = 'Input Numérico', 
        on_change = None, 
        args = None, 
        kwargs = None, 
        disabled = False, 
        label_visibility = "visible")
            
          

#Criar um DataFrame com os inputs exatamente igual ao dataframe em que foi treinado o modelo
if c:
    desabilita_preditores()
    
#Usar o modelo salvo para fazer previsao nesse Dataframe

st.divider()

prever = pd.DataFrame(load())
st.write(prever)

_, c1, _ = st.columns([1,3,1])


with c1:
	botao = st.button('Prever se o piloto pontuou',
		type = 'primary',
		use_container_width = True)

st.divider()

if botao:
    previsao = predict_model(modelo, data = prever)
    
    #st.write(type(previsao.loc[0,'prediction_label']))
    if previsao.loc[0,'prediction_label']:
        resultado = "pontuou"
    else:
        resultado = "não pontuou"
    
    st.header('O piloto {}'.format(resultado))
