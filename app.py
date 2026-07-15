# -*- coding: utf-8 -*-
#Created on Tue Jul 14 11:20:39 2026

#@author: rafae

import streamlit as st
import spacy
import os
from typing import List
from pydantic import BaseModel, Field
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# =====================================================================
# CONFIGURAÇÕES DA PÁGINA (Deve ser o primeiro comando Streamlit)
# =====================================================================
st.set_page_config(
    page_title="MedAudit IA - Auditor de Prontuários",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================================
# LÓGICA DE BACKEND (NLP & IA)
# =====================================================================

# Carrega o modelo de português do SpaCy com cache
@st.cache_resource
def carregar_nlp():
    try:
        return spacy.load("pt_core_news_sm")
    except OSError:
        import os
        os.system("python -m spacy download pt_core_news_sm")
        return spacy.load("pt_core_news_sm")

nlp = carregar_nlp()

def desidentificar_texto(texto: str) -> str:
    # Remove nomes próprios do texto do prontuário para conformidade com a LGPD
    doc = nlp(texto)
    texto_limpo = texto
    for ent in reversed(doc.ents):
        if ent.label_ == "PER":
            texto_limpo = texto_limpo[:ent.start_char] + "[PACIENTE]" + texto_limpo[ent.end_char:]
    return texto_limpo

# Estruturação de dados com Pydantic usando aspas simples/duplas normais
class AlertaClinico(BaseModel):
    tipo: str = Field(description="Categoria do erro (ex: Dosagem, Contradição Clínica, Omissão, Erro Técnico)")
    trecho_original: str = Field(description="O texto exato do prontuário que contém o erro")
    correcao_sugerida: str = Field(description="A redação correta ou a conduta sugerida")
    justificativa: str = Field(description="A explicação clínica ou técnica de por que isso está errado")

class RelatorioAuditoria(BaseModel):
    alertas: List[AlertaClinico] = Field(description="Lista de todas as inconsistências identificadas")
    prontuario_corrigido: str = Field(description="O texto do prontuário totalmente reescrito e corrigido profissionalmente")

import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI # Importação moderna do Gemini

import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError

import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import ValidationError

def analisar_prontuario(prontuario_texto: str):
    # Inicializa a variável como None para evitar qualquer NameError no retorno
    resultado = None
    
    # 1. Recupera a chave de API de forma segura
    try:
        api_key = st.secrets["GEMINI_API_KEY"]
    except KeyError:
        st.error("A chave 'GEMINI_API_KEY' não foi encontrada nos Secrets do Streamlit.")
        return None

    try:
        # 2. Inicializa o modelo Gemini diretamente
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.1
        )
        
        # 3. Força a saída estruturada com o seu modelo Pydantic (RelatorioAuditoria)
        llm_com_estrutura = llm.with_structured_output(RelatorioAuditoria)
        
        # 4. Cria a cadeia (certifique-se de que prompt_auditoria está definido no seu app.py)
        cadeia_analise = prompt_auditoria | llm_com_estrutura
        
        # 5. Executa a requisição
        resultado = cadeia_analise.invoke({"prontuario": prontuario_texto})
        
    except ValidationError as val_err:
        st.error(f"Erro de validação nos dados retornados pela IA: {val_err}")
    except Exception as e:
        st.error(f"Erro interno no processamento com o Gemini: {e}")
        
    return resultado

    except ValidationError as val_err:
        st.error(f"Erro de validação nos dados retornados pela IA: {val_err}")
        return None
    except Exception as e:
        st.error(f"Erro interno no processamento com o Gemini: {e}")
        return None
    
    instrucoes_sistema = (
        "Você é um auditor médico altamente experiente e especialista em revisão de prontuários eletrônicos (PEP). "
        "Sua tarefa é analisar o prontuário fornecido e identificar erros graves como: "
        "1. Inconsistências de dosagem de medicamentos. "
        "2. Contradições clínicas. "
        "3. Omissão de CIDs essenciais ou exames críticos. "
        "4. Prescrição de alérgenos conhecidos. "
        "5. Erros de terminologia médica. "
        "Retorne a resposta estritamente no formato JSON estruturado solicitado."
    )
    
    prompt_auditoria = ChatPromptTemplate.from_messages([
        ("system", instrucoes_sistema),
        ("user", "Por favor, analise e corrija o seguinte prontuário:\n\n{prontuario}")
    ])
    
    cadeia = prompt_auditoria | llm_estruturado
    return cadeia.invoke({"prontuario": prontuario_texto})

# =====================================================================
# INTERFACE GRÁFICA (STREAMLIT)
# =====================================================================

# Barra Lateral (Sidebar) para configurações de API e Exemplos
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/387/387561.png", width=80)
    st.title("Configurações")
    
    api_key_input = st.text_input(
        "Chave de API OpenAI",
        type="password",
        placeholder="sk-...",
        help="Sua chave não é salva em nenhum servidor externo, rodando apenas nesta sessão."
    )
    
    st.markdown("---")
    st.subheader("Exemplos para Teste")
    exemplo_selecionado = st.selectbox(
        "Escolha um cenário comum de erro:",
        [
            "Caso 1: Superdosagem e Alergia",
            "Caso 2: Contradição de Sinais Vitais",
            "Nenhum (Limpar)"
        ]
    )

# Definindo os textos de exemplos baseados na escolha do usuário
prontuario_exemplo = ""
if exemplo_selecionado == "Caso 1: Superdosagem e Alergia":
    prontuario_exemplo = (
        "Paciente Rafael Silva, 32 anos, deu entrada queixando-se de cefaleia intensa. "
        "Ao exame físico, apresenta-se afebril. "
        "Foi administrado dipirona 50g via oral. "
        "Paciente refere alergia conhecida a dipirona."
    )
elif exemplo_selecionado == "Caso 2: Contradição de Sinais Vitais":
    prontuario_exemplo = (
        "A paciente Julia Costa, 45 anos, relata dor abdominal difusa. "
        "Ao exame clínico: abdômen flácido, indolor à palpação, ruídos hidroaéreos presentes. "
        "Paciente apresenta febre alta com temperatura registrada de 36.2°C. "
        "Prescrito Tramadol para controle de dor intensa no abdômen doloroso."
    )

# Área Principal
st.title("🩺 MedAudit IA")
st.caption("Sistema Inteligente de Auditoria, Higienização LGPD e Correção de Prontuários Clínicos")
st.markdown("---")

# Layout de duas colunas na entrada
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. Entrada do Prontuário")
    texto_prontuario = st.text_area(
        "Cole aqui a evolução clínica original do paciente:",
        value=prontuario_exemplo,
        height=200,
        placeholder="Paciente XPTO..."
    )

with col2:
    st.subheader("2. Higienização de Dados (LGPD)")
    st.caption("Remoção automática de dados pessoais identificáveis (PII) em tempo real.")
    
    if texto_prontuario:
        texto_seguro = desidentificar_texto(texto_prontuario)
        st.info(texto_seguro)
    else:
        st.info("Aguardando inserção do prontuário na coluna ao lado...")
        texto_seguro = ""

# Botão de execução
st.markdown("<br>", unsafe_allow_html=True)
processar_botao = st.button("🚀 Auditar Prontuário com IA", use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

# Processamento e exibição de resultados (Versão para IA Local)
if processar_botao:
    if not texto_seguro.strip():
        st.error("❌ O prontuário está vazio ou não possui conteúdo válido para auditoria.")
    else:
        with st.spinner("Analisando inconsistências clínicas localmente..."):
            try:
                # Agora chamamos a função sem precisar validar a chave da OpenAI
                resultado_analise = analisar_prontuario(texto_seguro)
                
                st.subheader("🔍 Relatório de Auditoria Gerado")
                
                if resultado_analise.alertas:
                    st.error(f"🚨 {len(resultado_analise.alertas)} Alertas de Inconsistência Encontrados!")
                    
                    for idx, alerta in enumerate(resultado_analise.alertas, 1):
                        with st.expander(f"⚠️ Alerta #{idx} - {alerta.tipo}", expanded=True):
                            st.write(f"**Trecho com inconsistência:** {alerta.trecho_original}")
                            st.write(f"**Sugestão de correção:** {alerta.correcao_sugerida}")
                            st.markdown(f"**Justificativa Técnica/Clínica:** {alerta.justificativa}")
                else:
                    st.success("✅ Nenhum erro grave ou inconsistência clínica foi detectado no prontuário!")
                
                st.markdown("---")
                
                st.subheader("✍️ Sugestão de Prontuário Corrigido")
                st.text_area(
                    "O médico responsável pode revisar, copiar ou aprovar a alteração:",
                    value=resultado_analise.prontuario_corrigido,
                    height=180,
                    disabled=False
                )
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("✅ Aprovar e Atualizar no PEP", type="primary", use_container_width=True):
                        st.success("Salvo com sucesso no prontuário eletrônico!")
                with col_btn2:
                    if st.button("❌ Descartar Alterações", use_container_width=True):
                        st.info("Alterações descartadas pelo profissional.")
                
            except Exception as e:
                st.error(f"Erro ao processar a requisição: {e}")