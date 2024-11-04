from flask import Flask, request, jsonify, render_template, send_from_directory
import os
import requests
import pdfkit

app = Flask(__name__)

# URL e token de autorização fornecidos
ANYTHING_LLM_URL = "http://localhost:3001/api/v1/workspace/robot/chat"
AUTH_TOKEN = "Y0S7Z8X-5P84THA-G7EQBD1-ZTFN6CT"  # Token de autenticação fornecido

# Diretório para salvar os arquivos gerados
OUTPUT_DIR = os.path.join(os.getcwd(), 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_response_from_anything_llm(prompt, session_id="identifier-to-partition-chats-by-external-id"):
    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Content-Type": "application/json"
    }
    
    data = {
        "message": prompt,
        "mode": "chat",
        "sessionId": session_id
    }

    try:
        response = requests.post(ANYTHING_LLM_URL, json=data, headers=headers)
        response.raise_for_status()
        
        response_json = response.json()
        content = response_json.get("textResponse", "Nenhuma resposta encontrada.")
        return content
    
    except requests.exceptions.HTTPError as http_err:
        print(f"Erro HTTP ao conectar ao AnythingLLM: {http_err}")
        return "Desculpe, ocorreu um erro ao tentar obter uma resposta."
    except Exception as err:
        print(f"Erro inesperado: {err}")
        return "Desculpe, ocorreu um erro ao tentar obter uma resposta."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/gerar_avaliacao', methods=['POST'])
def gerar_avaliacao():
    data = request.json
    questoes = data['questoes']
    nivel_dificuldade = data['nivel_dificuldade']
    tema = data['tema']
    texto_exemplo = data['texto_exemplo']
    formato_saida = data['formato_saida']

    prompt = (f"Preciso de uma lista de {questoes} questões objetivas com alternativas (A, B, C, D, E) "
              f"para testar a compreensão sobre o tema: {tema}. "
              f"Crie perguntas de múltipla escolha com base no seguinte texto: {texto_exemplo}. "
              f"Inclua o gabarito com as respostas corretas. As perguntas devem ser de nível {nivel_dificuldade}.")

    output = get_response_from_anything_llm(prompt)
    
    if formato_saida.lower() == "pdf":
        file_path = os.path.join(OUTPUT_DIR, "avaliacao.pdf")
        pdfkit.from_string(output, file_path)
    else:
        file_path = os.path.join(OUTPUT_DIR, "avaliacao.txt")
        with open(file_path, "w") as f:
            f.write(output)
    
    return jsonify({"message": "Avaliação gerada com sucesso!", "file_path": file_path})

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(OUTPUT_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)
