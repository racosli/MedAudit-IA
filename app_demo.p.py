# -*- coding: utf-8 -*-
#"""
#Created on Tue Jul 14 20:39:47 2026

#@author: rafae
#"""

import streamlit as st
import os
# Usando a biblioteca padrão da OpenAI ou LangChain para o deploy
from langchain_openai import ChatOpenAI 

def analisar_prontuario(prontuario_texto: str) -> RelatorioAuditoria:
    # O Streamlit Cloud vai ler a chave de API diretamente das configurações seguras (Secrets)
    api_key = st.secrets["OPENAI_API_KEY"]
    
    # Inicializa o modelo usando a API na nuvem
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=api_key, temperature=0.1)
    llm_estruturado = llm.with_structured_output(RelatorioAuditoria)
    
    # ... resto do seu código de prompt ...
    cadeia = prompt_auditoria | llm_estruturado
    return chain.invoke({"prontuario": prontuario_texto})