# MedAudit IA - Auditor Inteligente de Prontuários Eletrônicos

O **MedAudit IA** é um assistente inteligente de auditoria clínica, higienização de dados (LGPD) e correção de prontuários eletrônicos de pacientes (PEP). 

O sistema foi desenhado para atuar como um co-piloto ("Human-in-the-loop") para profissionais de saúde e auditores, identificando inconformidades graves que impactam diretamente a segurança do paciente e o faturamento hospitalar (evitando glosas médicas).

---

##  Diferenciais do Projeto

* **Privacidade Absoluta (LGPD):** O sistema utiliza IA local (via Ollama) e algoritmos de desidentificação de dados pessoais identificáveis (PII) para garantir que nenhuma informação sensível de saúde saia do ambiente do hospital.
* **Detecção Avançada de Inconsistências:** Identifica automaticamente erros de dosagem, contradições clínicas (ex: relatar paciente afebril com temperatura registrada de 39°C) e prescrições de potenciais alérgenos.
* **Interface Dinâmica:** Interface gráfica amigável desenvolvida em Streamlit para simulação e tomada de decisão médica em tempo real.

---

##  Tecnologias Utilizadas

* **Linguagem:** Python
* **Interface:** [Streamlit](https://streamlit.io/)
* **Orquestração de IA:** [LangChain](https://www.langchain.com/) / [LangChain-Ollama](https://github.com/langchain-ai/langchain-ollama)
* **Motor de IA Local:** [Ollama](https://ollama.com/) (Modelo `llama3` ou `llama3.2`)
* **Mascaramento LGPD:** [SpaCy](https://spacy.io/) (Modelo `pt_core_news_sm` para NLP em Português)

---

##  Como Rodar o Projeto Localmente

### Pré-requisitos
1. Certifique-se de ter o **Python 3.10+** instalado.
2. Baixe e execute o **[Ollama](https://ollama.com/)** no seu computador.
3. No seu terminal, faça o download do modelo local utilizado:
   ```bash
   ollama run llama3