# Use a imagem oficial do Java como base
FROM openjdk:11-jre-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie seu código e o arquivo JAR do Tabula para o container
COPY . /app

# Exponha a porta que o Flask vai usar
EXPOSE 5000

# Instalar dependências do Python
RUN apt-get update -y && apt-get install -y \
    python3 \
    python3-pip \
    openjdk-11-jre-headless \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependências do Python
RUN pip3 install --no-cache-dir -r requirements.txt

# Comando para rodar o seu código Python com o Flask e o Tabula
CMD ["sh", "-c", "java -jar tabula.jar & python3 /app.py"]
