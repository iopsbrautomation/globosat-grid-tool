# 📺 Gerador de Grade Globosat

Este projeto é uma ferramenta de automação desenvolvida para facilitar a extração e conversão das grades de programação da Globo/Globosat (ambientes Planning e Composite).

A ferramenta acessa a API oficial da emissora, processa os dados brutos (JSON) e gera um arquivo Excel formatado e pronto para uso pelas equipes internas.

## 🚀 Funcionalidades

* **Autenticação Automática:** Gera tokens temporários de acesso à API da Globo.
* **Consulta Flexível:** Permite selecionar entre os ambientes *Planning* e *Composite*.
* **Catálogo de Canais:** Exibe a lista atualizada de códigos de canais disponíveis.
* **Exportação Excel:** Converte o JSON complexo da API em uma planilha Excel amigável, aplicando automaticamente um template padrão.

## 🛠️ Tecnologia Utilizada: Streamlit

Este projeto foi construído utilizando **Streamlit**, uma tecnologia que transforma scripts de dados em aplicações web interativas.

**Por que Streamlit?**
Diferente de scripts tradicionais que rodam apenas em terminais ou notebooks (como o Colab), o Streamlit nos permite criar uma interface visual amigável (botões, calendários, tabelas) mantendo toda a inteligência de dados do Python (Pandas) no backend. Isso democratiza o acesso à automação: qualquer pessoa da equipe pode usar a ferramenta através do navegador, sem precisar saber programar.

## 📦 Como Executar Localmente

Caso precise rodar a aplicação em sua própria máquina para desenvolvimento:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU-USUARIO/globosat-grid-tool.git](https://github.com/SEU-USUARIO/globosat-grid-tool.git)
    ```

2.  **Instale as dependências:**
    Certifique-se de ter o Python instalado e rode:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Configuração de Segurança (Importante):**
    Este projeto requer credenciais de API que **não** estão incluídas no repositório por segurança. Crie um arquivo `.streamlit/secrets.toml` na raiz do projeto com o seguinte formato:
    ```toml
    API_KEY = "sua_chave_aqui"
    CLIENT_SECRET = "seu_segredo_aqui"
    CLIENT_ID = "seu_id_aqui"
    RESOURCE_ID = "seu_resource_id_aqui"
    ```

4.  **Inicie o App:**
    ```bash
    streamlit run app.py
    ```

## 🔒 Segurança

As credenciais de acesso (Client ID/Secret) são gerenciadas através dos **Streamlit Secrets** e nunca são expostas no código fonte público.

---
**Desenvolvido por IOPS BR @ Gracenote**
