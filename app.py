import streamlit as st
import requests
import pandas as pd
from datetime import datetime
import io

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="Gerador de Grade Globo/Globosat", 
    page_icon="📺",
    layout="centered"
)

# ==============================================================================
# SEGREDOS
# ==============================================================================
try:
    API_KEY = st.secrets["API_KEY"]
    CLIENT_SECRET = st.secrets["CLIENT_SECRET"]
    CLIENT_ID = st.secrets["CLIENT_ID"]
    RESOURCE_ID = st.secrets["RESOURCE_ID"]
except FileNotFoundError:
    st.error("Arquivo de segredos não encontrado! Verifique o .streamlit/secrets.toml")
    st.stop()

# ==============================================================================
# COLUNAS DO TEMPLATE
# ==============================================================================
TEMPLATE_COLUMNS = [
    'scheduledDate', 'program|startTime', 'firstExhibition', 'duration',
    'title|duration', 'program|duration', 'showName', 'name', 'title|showName',
    'program|synopsis', 'title|synopsis', 'title|aka', 'title|name',
    'title|season|number', 'title|episodeNumber', 'title|versionCertification',
    'title|versionCertificationConfirmed', 'title|versionSubCertification',
    'title|countries', 'title|yearOfProduction', 'contentType',
    'title|genre|name', 'title|subgenre|name', 'category', 'live',
    'title|resolution', 'title|audios|language', 'title|audios|type',
    'title|directors|name', 'title|cast|name', 'title|mainActors|name',
    'program|name', 'composite', 'title|nationalContent',
    'title|qualifiedContent', 'title|independentProduction', 'id', 'txId',
    'title|id', 'title|registrationNumber', 'title|purchaseId',
    'title|versionId', 'title|season|id', 'title|season|name',
    'title|genre|id', 'title|subgenre|id', 'program|id',
    'program|weekDays|sunday', 'program|weekDays|monday',
    'program|weekDays|tuesday', 'program|weekDays|wednesday',
    'program|weekDays|thursday', 'program|weekDays|friday',
    'program|weekDays|saturday', 'clauses|id', 'clauses|name',
    'clauses|startDate', 'clauses|endDate'
]

# ==============================================================================
# FUNÇÕES
# ==============================================================================
@st.cache_data(ttl=3000) 
def gerar_token():
    url = "https://login.microsoftonline.com/a7cdc447-3b29-4b41-b73e-8a2cb54b06c6/oauth2/token"
    headers = {'Content-Type': 'application/x-www-form-urlencoded', 'x-api-key': API_KEY}
    query_params = {'X-Api-Key': API_KEY}
    body_data = {
        'grant_type': 'client_credentials',
        'client_secret': CLIENT_SECRET,
        'client_id': CLIENT_ID,
        'resource': RESOURCE_ID
    }
    try:
        response = requests.post(url, headers=headers, params=query_params, data=body_data)
        response.raise_for_status()
        return response.json().get('access_token')
    except Exception as e:
        st.error(f"Erro ao gerar token: {e}")
        return None

@st.cache_data
def obter_channel_codes(token):
    url = "https://apis.g.globo/grids/v1/channels"
    headers = {'Authorization': f'Bearer {token}', 'x-api-key': API_KEY}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao buscar lista de canais: {e}")
        return None

def obter_grid_data(token, environment, channel_code, start, end):
    if environment == 'Planning':
        url = "https://apis.g.globo/grids/v1/epg"
    else:
        url = "https://apis.g.globo/grids/v1/external/slots/"
        
    headers = {'Authorization': f'Bearer {token}', 'x-api-key': API_KEY}
    params = {'ChannelCode': channel_code, 'StartDate': start, 'EndDate': end}
    
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao buscar a grade: {e}")
        return None

# ==============================================================================
# COMPONENTES DE UI
# ==============================================================================
def criar_sidebar():
    with st.sidebar:
        st.header("ℹ️ Sobre o App")
        st.info(
            """
            Este aplicativo conecta-se à API da Globo/Globosat para buscar 
            a grade de programação (Planning ou Composite) e converte o JSON em Excel.
            
            **Como usar:**
            1. Escolha o ambiente e o canal.
            2. Defina as datas de início e fim.
            3. Clique em **Gerar Grade Excel**.
            """
        )
        st.markdown("---")
        st.caption("Versão 1.1 - Jan/2026")

def criar_footer():
    st.markdown("---")
    # CSS para centralizar e estilizar o footer
    st.markdown(
        """
        <div style='text-align: center; color: grey; font-size: small;'>
            Desenvolvido por <b>IOPS BR @ Gracenote, a Nielsen Company</b>
        </div>
        """, 
        unsafe_allow_html=True
    )

# ==============================================================================
# APP PRINCIPAL
# ==============================================================================
criar_sidebar()

st.title("📺 Gerador de Grade Globo/Globosat")
st.markdown("Preencha os campos abaixo para gerar a grade em Excel.")

with st.spinner("Autenticando com a Globo..."):
    token = gerar_token()

if token:
    channels_data = obter_channel_codes(token)
    
    if channels_data:
        df_channels = pd.DataFrame(channels_data)
        
        if 'code' in df_channels.columns and 'name' in df_channels.columns:
            df_display = df_channels[['code', 'name']].rename(columns={
                'code': 'Código', 
                'name': 'Nome'
            })
            
            st.expander("Canais Disponíveis (Referência)", expanded=False).dataframe(
                df_display.sort_values('Código'),
                use_container_width=True,
                hide_index=True
            )

    col1, col2 = st.columns(2)
    
    with col1:
        env_option = st.radio("Ambiente", ["Planning", "Composite"])
        channel_list = [c['code'] for c in channels_data] if channels_data else []
        selected_channel = st.selectbox("Código do Canal", channel_list)

    with col2:
        start_date = st.date_input("Data Início", value=datetime.now())
        end_date = st.date_input("Data Fim", value=datetime.now())

    if st.button("Gerar Grade Excel", type="primary"):
        if not selected_channel:
            st.warning("Por favor, selecione um canal.")
        else:
            with st.spinner('Buscando dados e convertendo...'):
                raw_data = obter_grid_data(token, env_option, selected_channel, start_date, end_date)
                
                if raw_data:
                    try:
                        # 1. PREPARAR LISTA DE DADOS
                        dados_para_processar = []
                        
                        if env_option == 'Planning':
                            for day_schedule in raw_data:
                                if 'slots' in day_schedule and isinstance(day_schedule['slots'], list):
                                    dados_para_processar.extend(day_schedule['slots'])
                        else:
                            dados_para_processar = raw_data

                        # 2. INCLUSÃO DE CLAUSES
                        # Remove a lista e deixa apenas o primeiro objeto 'clause'
                        for item in dados_para_processar:
                            if 'clauses' in item and isinstance(item['clauses'], list):
                                if len(item['clauses']) > 0:
                                    item['clauses'] = item['clauses'][0]
                                else:
                                    del item['clauses']

                        # 3. NORMALIZAÇÃO E EXPORTAÇÃO
                        df_normalized = pd.json_normalize(dados_para_processar, sep='|')
                        
                        if df_normalized is not None and not df_normalized.empty:
                            df_final = df_normalized.reindex(columns=TEMPLATE_COLUMNS)
                            
                            buffer = io.BytesIO()
                            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                                df_final.to_excel(writer, index=False)
                            
                            st.success(f"✅ Grade gerada com sucesso para {selected_channel}!")
                            
                            st.download_button(
                                label="📥 Baixar Arquivo Excel",
                                data=buffer.getvalue(),
                                file_name=f"{env_option}_{selected_channel}_{start_date}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )
                        else:
                            st.warning("A API retornou dados, mas a grade estava vazia após o processamento.")
                    except Exception as e:
                        st.error(f"Erro ao processar os dados: {e}")
                else:
                    st.warning("Nenhum dado encontrado para este período.")

criar_footer()
