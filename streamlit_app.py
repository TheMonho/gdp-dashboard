import streamlit as st
import pandas as pd

# Configuração da página em modo amplo para caber a grade completa
st.set_page_config(page_title="Sistema GSAN", page_icon="🎵", layout="wide")

# Link de exportação direta em CSV para evitar erros de serviço de rede (DNS) do Google
ID_PLANILHA = "187NTVcRoa_6VJ-vSqyJFjic-OyJ25hU7g7akQQ2TpT8"
URL_BASE = f"https://google.com{ID_PLANILHA}/export?format=csv"

@st.cache_data(ttl=5) # Atualiza rápido para testes (5 segundos)
def puxar_dados_diretos():
    try:
        # Puxa cada aba informando o GID exato coletado da sua planilha oficial
        prof = pd.read_csv(f"{URL_BASE}&gid=0").dropna(how='all')
        alun = pd.read_csv(f"{URL_BASE}&gid=527022067").dropna(how='all')
        agen = pd.read_csv(f"{URL_BASE}&gid=1410756770").dropna(how='all')
        inve = pd.read_csv(f"{URL_BASE}&gid=64547285").dropna(how='all')
        return prof, alun, agen, inve
    except Exception as e:
        st.error(f"Erro na leitura direta: {e}")
        return None, None, None, None

df_prof, df_alunos, df_agenda, df_inventario = puxar_dados_diretos()

st.title("🎵 SISTEMA GSAN")

if df_prof is None or df_prof.empty:
    st.error("Não conseguimos ler a aba PROFESSORES. Certifique-se de que a planilha está pública para leitura.")
else:
    # Limpa espaços invisíveis nos nomes das colunas
    df_prof.columns = df_prof.columns.str.strip()
    
    aba_visao, aba_admin = st.tabs(["👁️ Visão da Grade (Professor)", "⚙️ Painel do Administrador (Seu Controle)"])

    with aba_visao:
        st.subheader("Grade Horária Semanal")
        
        # Garante a leitura correta independente de maiúsculas ou minúsculas
        col_prof_nome = 'NOME DO PROFESSOR' if 'NOME DO PROFESSOR' in df_prof.columns else df_prof.columns
        lista_professores = df_prof[col_prof_nome].dropna().tolist()
        
        professor_selecionado = st.selectbox("Selecione o Professor:", lista_professores)
        
        # Cria a matriz padrão da grade horária (08:00 às 21:00)
        dias_semana = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"]
        horarios_escola = [f"{hora:02d}:00" for hora in range(8, 22)]
        matriz_grade = pd.DataFrame("-", index=dias_semana, columns=horarios_escola)
        
        # Processa a agenda real vinda da sua planilha
        if df_agenda is not None and not df_agenda.empty:
            df_agenda.columns = df_agenda.columns.str.strip()
            
            col_ag_prof = 'PROFESSOR' if 'PROFESSOR' in df_agenda.columns else df_agenda.columns
            agenda_filtrada = df_agenda[df_agenda[col_ag_prof].astype(str).str.strip().str.lower() == str(professor_selecionado).strip().str.lower()]
            
            for idx, linha in agenda_filtrada.iterrows():
                dia = str(linha.get('DIA DA SEMANA', '')).strip()
                hor = str(linha.get('HORÁRIO', '')).strip()
                if len(hor) == 4: hor = "0" + hor # Padroniza 8:00 para 08:00
                
                if dia in dias_semana and hor in horarios_escola:
                    matriz_grade.at[dia, hor] = f"👤 {linha.get('ALUNO', '')} ({linha.get('SALA', '')})"
        
        # Desenha a tabela limpa na tela
        st.dataframe(matriz_grade, use_container_width=True)
        st.success("✅ Conectado com sucesso à sua planilha oficial Google Sheets!")
