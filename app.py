import os
import io
from flask import Flask, request, render_template
import pandas as pd
import tabula
import re  # Importando para usar expressões regulares
from unidecode import unidecode  # Importando a função para remover acentuação
import subprocess

app = Flask(__name__)
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


# Define as turmas fora das funções
turmas = [f"{i}{j}" for i in range(2, 6) for j in ['A', 'B', 'C', 'D', 'E', 'F', 'G']]

# Mapeamento entre as turmas e os números das planilhas
turma_to_sheet = {
    "2A": 3, "2B": 4, "2C": 5, "2D": 6, "2E": 7, "2F": 8,
    "3A": 9, "3B": 10, "3C": 11, "3D": 12, "3E": 13, "3F": 14,
    "4A": 15, "4B": 16, "4C": 17, "4D": 18, "4E": 19, "4F": 20, "4G": 21,
    "5A": 22, "5B": 23, "5C": 24, "5D": 25, "5E": 26, "5F": 27, "5G": 28
}

def run_java_code():
    try:
        # Compilar o código Java
        subprocess.run(['javac', 'MyJavaApp.java'], check=True)
        
        # Executar o código Java
        result = subprocess.run(['java', 'MyJavaApp'], capture_output=True, text=True, check=True)
        
        # Retornar o resultado da execução
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Erro ao rodar Java: {e}"

@app.route('/run-java')
def run_java():
    java_output = run_java_code()
    return render_template('index.html', java_output=java_output)

# Função para extrair os nomes do Excel, com base na turma selecionada
def extract_names_and_observations_from_excel(excel_file, turma):
    # Obtenha o número da planilha a partir da turma
    sheet_number = turma_to_sheet.get(turma)
    
    # Verifica se a turma está no dicionário
    if not sheet_number:
        raise ValueError(f"Turma {turma} não encontrada no mapeamento.")
    
    # Lê a planilha específica com base no número
    df = pd.read_excel(excel_file, sheet_name=sheet_number - 1, header=None)  # Sheets são indexadas a partir de 0
    
    # Extrai os nomes na coluna C (índice 2), começando da linha 10 (índice 9)
    names = df.iloc[9:, 2].dropna().tolist()
    
    # Extrai as observações da coluna H (índice 7), mas apenas nas linhas que não são NaN
    observations = df.iloc[9:, 7].dropna().tolist()
    
    # Ajuste para garantir que as observações estão associadas corretamente
    observations_dict = {}
    for index, observation in zip(df.iloc[9:, 7].dropna().index, observations):
        observations_dict[index] = observation

    # Agora vamos associar as observações aos nomes corretamente
    student_observations = []
    for i, name in enumerate(names):
        # Pega a observação da linha correspondente ao nome
        observation = observations_dict.get(i + 9, "")  # A linha real começa da linha 10 (índice 9)
        student_observations.append((name, observation))

    # Verificando as observações associadas corretamente
    print("Nomes e Observações extraídas do Excel:")
    for i, (name, obs) in enumerate(student_observations):
        print(f"{i + 1}. Nome: {name}, Observação: {obs}")
    
    return names, student_observations



# Função para corrigir nomes (corrige espaços e remove acentos/apóstrofos)
def correct_name_format(name):
    if not isinstance(name, str):
        return name  # Retorna como está caso não seja string
    
    # Remove caracteres especiais como '\r', '\n'
    name = re.sub(r'[\r\n]', ' ', name)  
    
    # Inserir espaços entre palavras maiúsculas e minúsculas coladas
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
    
    # Padroniza apóstrofos para um único tipo e remove todos
    name = re.sub(r"[‘’´`']", "", name)  # Remove todos os tipos de apóstrofos
    
    # Remove acentos
    name = unidecode(name)
    
    return name.strip()  # Remove espaços extras no início e no final

# Função para normalizar o nome (remover espaços, converter para minúsculas e remover acentuação)
def normalize_name(name):
    if name is None:
        return ""
    name = str(name).strip().lower()  # Converte para string, remove espaços e converte para minúsculas
    name = unidecode(name)  # Remove acentuação
    name = re.sub(r"[‘’´`']", "", name)  # Remove todos os tipos de apóstrofos  
    name = name.replace('\r', ' ').replace('\n', ' ')  # Substitui quebras de linha por espaço
    name = re.sub(r'\s+', ' ', name).strip()  # Remove múltiplos espaços consecutivos
    return name

# Função para extrair os nomes do PDF
def extract_names_and_situations_from_pdf(pdf_file):
    # Caminho para salvar o PDF temporariamente
    pdf_path = os.path.join(os.getcwd(), 'temp.pdf')  # Usando o diretório atual

    # Salva o arquivo PDF temporariamente
    pdf_file.save(pdf_path)
    
    # Converter PDF para CSV usando tabula
    tabula.convert_into(pdf_path, "output.csv", output_format="csv", pages='all')

    # Lê o CSV gerado
    df = pd.read_csv("output.csv")

    # Exibindo as primeiras linhas do CSV para depuração
    print("Cabeçalho do CSV (primeiras linhas):")
    print(df.head())  # Depuração

    # Verificando se a coluna "Situação" existe
    if 'Situação' in df.columns:
        # Extrai as situações (coluna K, index 10) e os nomes (coluna "Nome do Aluno", index 1)
        situations = df['Situação'].dropna().tolist()  # Considera apenas as linhas com situação
        names = df['Nome do Aluno'].dropna().tolist()  # Considera apenas as linhas com nome
        
        # Vamos criar uma lista de tuplas (Nome, Situação)
        names_and_situations = list(zip(names, situations))
    else:
        names_and_situations = []

    # Exibindo no log os nomes e as situações extraídas
    print("Nomes e Situação extraídas do PDF:")
    for i, (name, situation) in enumerate(names_and_situations):
        print(f"{i + 1}. Nome: {name}, Situação: {situation}")
    
    return names_and_situations

# Rota para renderizar o template de upload
@app.route('/')
def home():
    turmas = []
    for i in range(2, 6):
        for j in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
            turmas.append(f"{i}{j}")  # Gera 2A, 2B, 2C, ..., 5G
    return render_template('index.html', turmas=turmas)  # Envia as turmas de volta para o template

# Rota para comparar as listas e exibir resultados no template
@app.route('/compare', methods=['POST'])
def compare_lists():
    turma = request.form.get('turma')  # Captura a turma selecionada
    excel_file = request.files.get('excel')  # Captura o arquivo Excel
    pdf_file = request.files.get('pdf')  # Captura o arquivo PDF

    # Verifique se os arquivos e a turma foram recebidos corretamente
    if not turma:
        return render_template('index.html', error="Nenhuma turma selecionada.", turmas=turmas)
    
    if not excel_file or not pdf_file:
        return render_template('index.html', error="Por favor, envie ambos os arquivos Excel e PDF.", turmas=turmas)

    # Extrair nomes, observações e situações
    excel_names, excel_observations = extract_names_and_observations_from_excel(excel_file, turma)
    pdf_names_and_situations = extract_names_and_situations_from_pdf(pdf_file)

    # Verifique se as listas não estão vazias
    if not excel_names or not pdf_names_and_situations:
        return render_template('index.html', error="Uma das listas está vazia, verifique os arquivos.", turmas=turmas)

    # Normalizar os nomes
    normalized_excel_names = [normalize_name(name) for name in excel_names]
    print("Nomes do Excel depois de normalizar:", normalized_excel_names)

    # Criar um dicionário de nomes e situações do PDF com nomes normalizados
    pdf_dict = {}
    for name, situation in pdf_names_and_situations:
        normalized_name = normalize_name(name)
        pdf_dict[normalized_name] = situation

    print("Nomes e Situações do PDF:", pdf_dict)

    # Comparar e verificar divergências nas observações e situações
    divergencias = []

    for i, (excel_name, observation) in enumerate(zip(excel_names, excel_observations)):
        normalized_excel_name = normalize_name(excel_name)

        # Verifica se o nome do Excel existe no PDF
        if normalized_excel_name in pdf_dict:
            pdf_situation = pdf_dict[normalized_excel_name]  # Situação correspondente no PDF

            # Verifica se a situação é 'BXTR' ou 'Trans' e a observação não contém 'TE'
            if pdf_situation in ['BXTR', 'Trans'] and 'TE' not in observation:
                divergencias.append(f"Piloto:{excel_name},{observation}, Situação no SED: {pdf_situation}")
            
            # Verifica se a observação contém 'TE' e a situação é 'ATIVO'
            if 'TE' in observation and pdf_situation == 'ATIVO':
                divergencias.append(f"Piloto:{excel_name}, Observação: {observation}, Situação no SED: {pdf_situation}")
                
            # Verificar se a observação contém 'REM' no Excel e o nome correspondente não está no PDF
            if 'REM' in observation and normalize_name(excel_name) not in observation:
                divergencias.append(f"Piloto: Nome: {excel_name}, Observação: {observation}, Não encontrado REMA no SED")

            # Verificar se a situação no PDF é 'REMA' e o nome correspondente não está no Excel
            if 'REMA' in pdf_situation and normalize_name(excel_name) not in observation:
                divergencias.append(f"Piloto: Nome com 'REMA' no PDF: {excel_name}, Não encontrado REM na PILOTO")

    # Comparar os nomes exclusivos nas duas planilhas
    excel_set = set(normalized_excel_names)
    pdf_set = set(pdf_dict.keys())

    only_in_excel = excel_set - pdf_set  # Nomes que estão no Excel, mas não no PDF
    only_in_pdf = pdf_set - excel_set  # Nomes que estão no PDF, mas não no Excel

    # Exibir os resultados no log
    print("Nomes que estão apenas no Excel:", only_in_excel)
    print("Nomes que estão apenas no PDF:", only_in_pdf)

    # Exibir as divergências no log
    if divergencias:
        print("Divergências encontradas:")
        for divergencia in divergencias:
            print(divergencia)
    else:
        print("Nenhuma divergência encontrada.")

    # Exibir os resultados na interface web
    return render_template('index.html', 
                           divergencias=divergencias,  # Passa as divergências para o template
                           only_in_excel=list(only_in_excel),  # Passa os nomes exclusivos do Excel
                           only_in_pdf=list(only_in_pdf),  # Passa os nomes exclusivos do PDF
                           error=None, 
                           turmas=turmas)  # Passa as turmas para o template

if __name__ == '__main__':
    app.run(debug=True)
