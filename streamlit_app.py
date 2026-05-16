import streamlit as st
import pandas as pd

# Configuração da página em modo amplo para caber a grade completa
st.set_page_config(page_title="Sistema GSAN", page_icon="🎵", layout="wide")

# Usamos apenas o ID limpo da sua planilha para evitar erros de link quebrado
ID_PLANILHA = "187NTVcRoa_6VJ-vSqyJFjic-OyJ25hU7g7akQQ2TpT8"
BASE_URL = f"https://google.com{ID_PLANILHA}/gviz/tq?tqx=out:csv"

@st.cache_data(ttl=5) # Atualiza rápido para testes (5 segundos)
def puxar_dados_seguros():
    try:
        # Puxa cada aba informando o nome exato delas na planilha
        prof = pd.read_csv(f"{BASE_URL}&sheet=PROFESSORES").dropna(how='all')
        alun = pd.read_csv(f"{BASE_URL}&sheet=ALUNOS").dropna(how='all')
        agen = pd.read_csv(f"{BASE_URL}&sheet=AGENDA+FIXA").dropna(how='all')
        inve = pd.read_csv(f"{BASE_URL}&sheet=INVENTÁRIO").dropna(how='all')
        return prof, alun, agen, inve
    except Exception as e:
        st.error(f"Erro na leitura: {e}")
        return None, None, None, None

df_prof, df_alunos, df_agenda, df_inventario = puxar_dados_seguros()

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
        
        # Cria a matriz padrão da grade horária
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
