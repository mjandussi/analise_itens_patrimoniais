import pandas as pd
import streamlit as st
import re


######## CONFIG ###########

st.set_page_config(
    page_title="App Itens Patrimoniais",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


######## PÁGINAS ###########

def pagina_inicial():

    st.header("Seja bem vindo !!")
    st.header("Análises de Itens Patrimoniais do SIAFERIO")
    texto_com_cor = """
    <p>Esta aplicação web realiza a análise dos Itens Patrimoniais do SIAFERIO, facilitado a visualização das Naturezas de Despesas.</p>
    """
    st.markdown(texto_com_cor, unsafe_allow_html=True)


def analises():   

    st.header("Análises de Itens Patrimoniais")

    ### Coluna para os Arquivos
    st.write('Upload de Arquivos')
    upload_file1 = st.file_uploader('Lista de Itens Patrimoniais (arquivo XLSX)', type='xlsx')

    if upload_file1 is None:
        st.write('CARREGUE O ARQUIVO XLSX PARA CONTINUAR')

    else:

        itens_patrim = pd.read_excel(upload_file1, header=3, dtype=object)
        itens_patrim.drop(itens_patrim.tail(3).index, inplace=True)
        itens_despesa = itens_patrim.dropna(subset=['IMPLICA Despesa'])
        itens_despesa = itens_despesa.query('Ativo == "Sim"')
        itens_despesa.drop(['SE Despesa', 'SE Receita', 'IMPLICA Receita', 'Ativo', 'Tipo Ativo'], axis=1, inplace=True)
        # Dividir as string na coluna 'IMPLICA Despesa' por quebra de linha
        df_despesa = itens_despesa['IMPLICA Despesa'].str.split('\n', expand=True)

        # Reformata o DataFrame para ter cada item da String em uma nova linha
        df_dps = (
            itens_despesa
            .set_index(['Código', 'Nome', 'Código Tipo', 'Tipo', 'Subitem'])
            .apply(lambda row: row.str.split(r'\n| ou ? | OU ', regex=True).explode())
            .reset_index()
        )

        # Remover linhas com valores vazios na coluna 'IMPLICA Despesa'
        df_dps = df_dps[df_dps['IMPLICA Despesa'].str.strip() != '']

        # Remover onde 'IMPLICA Despesa' termina com um parêntese
        df_dps['IMPLICA Despesa'] = df_dps['IMPLICA Despesa'].str.rstrip(') ').str.strip()

        # Função dinâmica para substituir o padrão
        def substituir_codigo(text):
            start_match = re.search(r'começa com (\d+)', text)
            end_match = re.search(r'termina com (\d+)', text)

            if start_match and end_match:
                x = start_match.group(1)
                y = end_match.group(1)
                return f'{x}XX{y}'
            elif start_match:
                z = start_match.group(1)
                return f'{z}XX'
            elif end_match:
                w = end_match.group(1)
                return f'YYXX{w}'
            else:
                return text

        # Aplicando a função em cada linha do DataFrame
        df_dps['IMPLICA Despesa'] = df_dps['IMPLICA Despesa'].apply(substituir_codigo)


        # Função para pegar os últimos seis caracteres da string com espaços removidos
        def pegar_ultimos_seis_digitos(text):
            # Remover espaços em branco antes de capturar os últimos 6 caracteres
            text = text.replace(" ", "").replace("ou", "").replace("'", "").replace("OU", "")
            if len(text) >= 6:
                return text[-6:]
            return text

        # Aplicar a função em cada linha do DataFrame
        df_dps['ND'] = df_dps['IMPLICA Despesa'].apply(pegar_ultimos_seis_digitos)

       
        st.write(df_dps)


######## SIDEBAR ###########

# Menu de navegação na barra lateral
st.sidebar.title("Menu de Navegação")
opcao = st.sidebar.radio("Escolha a análise desejada:", ("Página Inicial", "Análise Itens Patrimoniais"))

# Chama a função correspondente à opção selecionada
if opcao == "Página Inicial":
    pagina_inicial()
elif opcao == "Análise Itens Patrimoniais":
    analises()