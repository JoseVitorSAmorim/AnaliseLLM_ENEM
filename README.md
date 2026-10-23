# AnaliseLLM_ENEM
Análise por LLM do conteúdo das quesõtes, do projeto de categorização das questões do ENEM de acordo com descritores e habilidades previstas da matriz de referência do exame. 
## Requisitos
- Python3
- API Gemini 2.5 Flash

## Ativando ambiente virtual
### Linux
```
python3 -m venv venv  
source venv/bin/activate  
```
### Windows
```
python -m venv venv
venv\Scripts\activate.ps1
```
## Instalar dependências
### Linux
Dê permissão
```
chmod +x install.sh
```
Para executar
```
./install.sh
```
> [!NOTE]
> Se seu Python for da versão 3.9 ou anterior e não conseguir baixar o google-genai, use isso:
```
pip install google-generativeai
```
### Windows
- Precisará rodar isso através do Git Bash (que costuma vir instalado junto com o Git)
- Clique com o botão direito na pasta do projeto e selecione "Open Git Bash here"
- Para executar
```
bash install.sh
```
## API
### Chave da API
Obter API key no Google AI Studio  
https://aistudio.google.com/app/api-keys

Adicione nas variável de ambiente com:
```
export GEMINI_API_KEY="SUA_CHAVE_AQUI"
```
