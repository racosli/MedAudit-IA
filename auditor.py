# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 11:10:08 2026

@author: rafae
"""

import spacy

# Carrega o modelo de português do SpaCy
nlp = spacy.load("pt_core_news_sm")

def desidentificar_texto(texto: str) -> str:
    """
    Detecta nomes próprios no texto do prontuário e os substitui por [PACIENTE]
    para proteger a privacidade antes de enviar à IA.
    """
    doc = nlp(texto)
    texto_limpo = texto
    
    # Busca por entidades que o SpaCy identifica como Pessoas (PER)
    for ent in reversed(doc.ents):
        if ent.label_ == "PER":
            texto_limpo = texto_limpo[:ent.start_char] + "[PACIENTE]" + texto_limpo[ent.end_char:]
            
    return texto_limpo

from typing import List, Optional
from pydantic import BaseModel, Field

class AlertaClinico(BaseModel):
    tipo: str = Field(description="Categoria do erro (ex: Dosagem, CID Inconsistente, Omissão, Erro Técnico)")
    trecho_original: str = Field(description="O texto exato do prontuário que contém o erro ou inconsistência")
    correcao_sugerida: str = Field(description="A redação correta ou a conduta sugerida")
    justificativa: str = Field(description="A explicação clínica ou técnica de por que isso está errado")

class RelatorioAuditoria(BaseModel):
    alertas: List[AlertaClinico] = Field(description="Lista de todas as inconsistências identificadas")
    prontuario_corrigido: str = Field(description="O texto do prontuário totalmente reescrito e corrigido profissionalmente")
    
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Configurando a chave de API (substitua pela sua ou defina no ambiente)
os.environ["OPENAI_API_KEY"] = "sua-chave-api-aqui"

# Inicializa o modelo de chat (usando o gpt-4o que é excelente para raciocínio clínico)
llm = ChatOpenAI(model="gpt-4o", temperature=0.1)

# Estrutura o parser para garantir o formato JSON desenhado no Passo 2
llm_estruturado = llm.with_structured_output(RelatorioAuditoria)

# Criando o Prompt de Sistema com as regras de negócio clínicas
prompt_auditoria = ChatPromptTemplate.from_messages([
    ("system", (
        "Você é um auditor médico altamente experiente e especialista em revisão de prontuários eletrônicos (PEP).\n"
        "Sua tarefa é analisar o prontuário fornecido e identificar erros graves como:\n"
        "- Inconsistências de dosagem de medicamentos (ex: doses pediátricas em adultos ou vice-versa).\n"
        "- Contradições clínicas (ex: relatar abdômen livre de dor e prescrever morfina para dor abdominal).\n"
        "- Omissão de CIDs essenciais ou exames críticos citados na evolução.\n"
        "- Erros de terminologia médica ou gramática clínica.\n\n"
        "Seja extremamente preciso. Se o prontuário não apresentar nenhum erro, retorne a lista de alertas vazia."
    )),
    ("user", "Por favor, analise e corrija o seguinte prontuário:\n\n{prontuario}")
])

# Cria a cadeia de execução (Chain)
cadeia_auditoria = prompt_auditoria | llm_estruturado

if __name__ == "__main__":
    # Exemplo de prontuário com problemas propositais
    prontuario_sujo = (
        "Paciente Rafael Silva, 32 anos, deu entrada queixando-se de cefaleia intensa. "
        "Ao exame físico, apresenta-se afebril, com temperatura de 39.5°C. "
        "Foi administrado dipirona 50g via oral. "
        "Paciente refere alergia a dipirona."
    )
    
    print("--- 1. Iniciando Desidentificação (LGPD) ---")
    prontuario_seguro = desidentificar_texto(prontuario_sujo)
    print(f"Prontuário Seguro: {prontuario_seguro}\n")
    
    print("--- 2. Enviando para Análise da IA ---")
    try:
        resultado: RelatorioAuditoria = cadeia_auditoria.invoke({"prontuario": prontuario_seguro})
        
        print("\n--- 3. Alertas Gerados pela Auditoria ---")
        for idx, alerta in enumerate(resultado.alertas, 1):
            print(f"\nAlerta #{idx} [{alerta.tipo}]:")
            print(f"  > Trecho: '{alerta.trecho_original}'")
            print(f"  > Sugestão: {alerta.correcao_sugerida}")
            print(f"  > Justificativa: {alerta.justificativa}")
            
        print("\n--- 4. Prontuário Sugerido (Corrigido) ---")
        print(resultado.prontuario_corrigido)
        
    except Exception as e:
        print(f"Ocorreu um erro no processamento: {e}")