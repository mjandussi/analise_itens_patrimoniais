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

def aplicar_filtros(df):
    # Lista de colunas para realizar filtros
    colunas = df.columns.tolist()

    # Dicionário para armazenar os valores escolhidos
    filtros = {}

    # Criar filtros dinâmicos para cada coluna
    for coluna in colunas:
        opcoes_coluna = df[coluna].dropna().unique().tolist()

        # Convertendo todas as opções para string para evitar problemas de comparação entre int e str
        opcoes_coluna = [str(opcao) for opcao in opcoes_coluna]
        opcoes_coluna.sort()  # Agora, é seguro ordenar

        # Adicionar as opções de filtro na barra lateral
        filtros[coluna] = st.sidebar.selectbox(f"Filtrar por {coluna}", ["Todos"] + opcoes_coluna)
    
    # Aplicar os filtros no DataFrame
    for coluna, valor in filtros.items():
        if valor != "Todos":
            df = df[df[coluna].astype(str) == valor]
    
    return df


def tabela_geral():   

    st.header("Tabela de Itens Patrimoniais")

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

        # Função para substituir o padrão
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
        itens_despesa['IMPLICA Despesa'] = itens_despesa['IMPLICA Despesa'].apply(substituir_codigo)

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

        # Função para pegar os últimos seis caracteres
        def pegar_digitos_para_nd(text):
            # Remove espaços e textos não especificados
            text = text.replace(" ", "").replace("ou", "").replace("'", "").replace("OU", "")
            
            # Retornar os caracteres desejados
            if len(text) > 10:
                return text[-6:]
            elif len(text) in [10, 8, 6]:
                return text[:6]
            return text

        # Aplicar no DataFrame
        df_dps['ND'] = df_dps['IMPLICA Despesa'].apply(pegar_digitos_para_nd)
        df_dps.drop(['IMPLICA Despesa'], axis=1, inplace=True)
        df_dps['Código'] = df_dps['Código'].astype(str)
        df_dps = df_dps.query('Subitem != "00"')

        # Filtrar dados
        df_dps_filtrado = aplicar_filtros(df_dps)

        # Armazena o DataFrame no session state
        st.session_state['df_dps_filtrado'] = df_dps_filtrado

        # Mostrar resultados
        st.write(df_dps_filtrado)


def analises():
    st.header("Análises dos Itens Patrimoniais")

    # Verifica se o DataFrame foi armazenado no session state
    if 'df_dps_filtrado' not in st.session_state:
        st.error("Por favor, primeiro carregue os dados na Tabela de Itens Patrimoniais.")
    else:
        df_dps_filtrado = st.session_state['df_dps_filtrado']

        # Análise de exemplo: tipos e NDs únicos
        tipos_disponiveis = df_dps_filtrado['Tipo'].unique().tolist()
        tipos_selecionados = st.sidebar.multiselect("Selecione o(s) Tipo(s) para análise:", tipos_disponiveis)

        if tipos_selecionados:
            df_selecionado = df_dps_filtrado[df_dps_filtrado['Tipo'].isin(tipos_selecionados)]
            nds_unicas_por_tipo = df_selecionado.groupby('Tipo')['ND'].unique().reset_index()
            nds_unicas_por_tipo['Número de NDs'] = nds_unicas_por_tipo['ND'].apply(len)

            st.write("NDs Únicas por Tipo:")
            st.write(nds_unicas_por_tipo)
        else:
            st.write("Selecione ao menos um Tipo para análise.")

######## SIDEBAR ###########

# Menu de navegação na barra lateral
st.sidebar.title("Menu de Navegação")
opcao = st.sidebar.radio("Escolha a análise desejada:", ("Página Inicial", "Tabela de Itens Patrimoniais", "Análises"))

# Página inicial
def pagina_inicial():
    st.header("Bem-vindo !!")
    st.header("Análise de Itens Patrimoniais do SIAFERIO")
    texto_com_cor = """
    <p>Esta aplicação web analisa os itens patrimoniais e as suas respectivas natureza de despesa no SIAFERIO, facilitando a visualização e filtragem da coluna IMPLICA DESPESA.</p>
    """
    st.markdown(texto_com_cor, unsafe_allow_html=True)

# Controlar qual função chamar
if opcao == "Página Inicial":
    pagina_inicial()
elif opcao == "Tabela de Itens Patrimoniais":
    tabela_geral()
elif opcao == "Análises":
    analises()