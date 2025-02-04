# Use a imagem oficial do Java como base
FROM openjdk:11-jre-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie seu código e o arquivo JAR do Tabula para o container
COPY . /app

# Exponha a porta que o Flask vai usar
EXPOSE 5000

# Instalar dependências do Python
RUN apt-get update && apt-get install -y python3 python3-pip
RUN pip3 install -r requirements.txt  # Se necessário, use o seu arquivo requirements.txt

# Comando para rodar o seu código Python com o Flask e o Tabula
CMD ["sh", "-c", "java -jar tabula.jar & python3 /app.py"]
