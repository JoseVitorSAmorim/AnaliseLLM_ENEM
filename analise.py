import os
import re
import json
import time
import google.generativeai as genai
from datetime import datetime

# ==================== CONFIGURAÇÕES ====================
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# Diretórios e arquivos
DIR_TEXTOS = "textos_extraidos"
DIR_SAIDA = "analises_geradas"
ARQUIVO_GABARITO = "gabarito.txt"
ARQUIVO_MATRIZ = "matriz_referencia_enem.json"
ARQUIVO_ESTRUTURA = "estrutura.json"

# ---------------------------------------------------------
# ✍️ PREENCHA COM OS SEUS DADOS E OS DADOS DO SEU CADERNO
# ---------------------------------------------------------
DADOS_ESTUDANTE = {
    "nome_completo": "José Vitor Santana de Amorim",
    "colegio": "CCM Marechal Rondon",
    "turma": "3B"
}

DADOS_CADERNO = {
    "ano": 2012,
    "dia": 2,                     # Ajuste para o dia correto (1 ou 2)
    "cor": "AMARELO",
    "aplicacao": "REGULAR"        # Ex: REGULAR, PPL, etc.
}
# ---------------------------------------------------------

# Configuração do Modelo
MODELO = 'gemini-3.8-flash'
generation_config = {"response_mime_type": "application/json"}
model = genai.GenerativeModel(model_name=MODELO, generation_config=generation_config)

# ==================== FUNÇÕES AUXILIARES ====================
def carregar_gabarito(caminho):
    gabarito = {}
    try:
        with open(caminho, 'r', encoding='utf-8') as f:
            for linha in f:
                match = re.search(r'(\d+)\s*[-–]\s*([A-E])', linha, re.IGNORECASE)
                if match:
                    num = int(match.group(1))
                    alt = match.group(2).upper()
                    gabarito[num] = alt
    except FileNotFoundError:
        print(f"Aviso: Arquivo {caminho} não encontrado.")
    return gabarito

def carregar_json(caminho):
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)

# ==================== PROMPT DO SISTEMA ====================
SUGESTION_PROMPT = """
Você é um analista especialista em questões do ENEM e em classificação segundo a Matriz de Referência do ENEM.

FONTES E HIERARQUIA:
1. O TXT da questão é a fonte primária do conteúdo, comando e alternativas.
2. matriz_referencia_enem.json é a fonte normativa para área, competência, habilidades, eixo cognitivo e objetos/conteúdos da Matriz.
3. gabarito.txt é a fonte oficial do gabarito quando houver correspondência.

REGRAS ABSOLUTAS:
- Não invente informações. Se não houver evidência, use null ou [].
- Nunca crie área, competência, habilidade ou eixo fora da matriz fornecida.
- Ao selecionar item da Matriz, copie ID e texto EXATAMENTE como estão na matriz.
- Nunca parafraseie, resuma ou corrija a redação da Matriz.
- A habilidade principal representa principalmente o que o estudante precisa fazer para resolver a questão, não apenas o assunto superficial.
- Considere comando + operação cognitiva + conteúdo + alternativas + correspondência com a Matriz.
- Habilidades relacionadas só entram quando houver evidência clara.
- Gabarito oficial tem prioridade sobre qualquer inferência da LLM.
- Sem gabarito oficial, correta deve permanecer null.
- Analise todas as alternativas presentes e não crie alternativas ausentes.
- Justificativas devem ser sustentadas pela questão.
- Não use conhecimento externo para preencher lacunas.
- OCR pode conter erros; corrija mentalmente apenas erros evidentes necessários à compreensão, sem inventar texto.
- Analise cada questão independentemente.
- Confiança: alta = correspondência clara; media = alguma ambiguidade; baixa = evidência insuficiente/ambígua.
- Retorne SOMENTE um JSON válido com a estrutura exata do schema fornecido. Preencha todos os campos, usando null se a informação não existir.

A CLASSIFICAÇÃO DE CONTEÚDO é analítica e não deve ser apresentada como se fosse redação oficial da Matriz.
"""

# ==================== EXECUÇÃO PRINCIPAL ====================
def main():
    print("Inicializando análise das questões...")
    
    os.makedirs(DIR_SAIDA, exist_ok=True)
    
    gabarito = carregar_gabarito(ARQUIVO_GABARITO)
    matriz_ref = carregar_json(ARQUIVO_MATRIZ)
    estrutura_base = carregar_json(ARQUIVO_ESTRUTURA)
    
    for arquivo in sorted(os.listdir(DIR_TEXTOS)):
        if not arquivo.endswith(".txt"):
            continue
            
        caminho_arquivo = os.path.join(DIR_TEXTOS, arquivo)
        
        match_num = re.search(r'questao-(\d+)', arquivo)
        if not match_num:
            continue
        numero_questao = int(match_num.group(1))
        resposta_correta = gabarito.get(numero_questao, "Não identificado")
        
        nome_arquivo_saida = arquivo.replace('.txt', '.json')
        caminho_saida = os.path.join(DIR_SAIDA, f"analise_{nome_arquivo_saida}")
        
        if os.path.exists(caminho_saida):
            print(f"Questão {numero_questao} já analisada. Pulando...")
            continue
            
        with open(caminho_arquivo, 'r', encoding='utf-8') as f:
            texto_questao = f.read()
            
        print(f"Analisando Questão {numero_questao}...")
        
        prompt_completo = f"""
        {SUGESTION_PROMPT}
        
        ESTRUTURA JSON EXIGIDA (Siga estritamente este formato):
        {json.dumps(estrutura_base, ensure_ascii=False, indent=2)}
        
        MATRIZ DE REFERÊNCIA (Use para consulta):
        {json.dumps(matriz_ref, ensure_ascii=False)}
        
        DADOS DA QUESTÃO ATUAL:
        Número da Questão: {numero_questao}
        Gabarito Oficial: {resposta_correta}
        Caminho do arquivo TXT: {caminho_arquivo}
        
        TEXTO DA QUESTÃO (Extraído via OCR):
        {texto_questao}
        """
        
        try:
            resposta = model.generate_content(prompt_completo)
            dados_analise = json.loads(resposta.text)
            
            # Injetar os dados do estudante no JSON retornado
            dados_analise['estudante'] = DADOS_ESTUDANTE
            
            # Injetar os dados da identificação do caderno
            dados_analise['questao']['identificacao_caderno']['ano'] = DADOS_CADERNO['ano']
            dados_analise['questao']['identificacao_caderno']['dia'] = DADOS_CADERNO['dia']
            dados_analise['questao']['identificacao_caderno']['cor'] = DADOS_CADERNO['cor']
            dados_analise['questao']['identificacao_caderno']['aplicacao'] = DADOS_CADERNO['aplicacao']
            
            # Atualizar metadados da IA na resposta
            dados_analise['auditoria_da_ia']['modelo'] = MODELO
            dados_analise['auditoria_da_ia']['datetime'] = datetime.now().isoformat()
            dados_analise['auditoria_da_ia']['proveniencia']['arquivo_questao'] = arquivo
            dados_analise['auditoria_da_ia']['proveniencia']['arquivo_matriz'] = ARQUIVO_MATRIZ
            
            with open(caminho_saida, 'w', encoding='utf-8') as f:
                json.dump(dados_analise, f, ensure_ascii=False, indent=4)
                
            print(f"✅ Sucesso! Salvo em: {caminho_saida}")
            
            time.sleep(3)
            
        except Exception as e:
            print(f"❌ Erro ao analisar a questão {numero_questao}: {e}")

    print("\nProcessamento finalizado!")

if __name__ == "__main__":
    main()