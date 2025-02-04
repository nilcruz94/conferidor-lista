# Use a imagem oficial do Python como base
FROM python:3.9-slim

# Defina o diretório de trabalho no container
WORKDIR /app

# Copie o conteúdo da pasta local (onde estão o app.py e tabula.jar) para o diretório /app no container
COPY . /app

# Exponha a porta que o Flask vai usar
EXPOSE 5000

# Instalar dependências do sistema e Python
RUN apt-get update && apt-get install -y python3 python3-pip openjdk-11-jre-headless

# Instalar dependências do Python
RUN pip3 install -r /app/requirements.txt

# Comando para rodar o Java e o Flask
CMD ["sh", "-c", "java -jar /app/tabula.jar & python3 /app/app.py"]
