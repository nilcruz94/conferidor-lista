# Usando uma imagem que já tem OpenJDK 11
FROM openjdk:11-jre-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie os arquivos para dentro do container
COPY . /app

# Instale o Python e outras dependências
RUN apt-get update && apt-get install -y python3 python3-pip

# Instalar dependências do Python
RUN pip3 install -r requirements.txt

# Expor a porta
EXPOSE 5000

# Comando para rodar o seu código
CMD ["sh", "-c", "java -jar tabula.jar & python3 app.py"]
