#!/bin/bash
echo "🕷️ INICIANDO INSTALAÇÃO DO ARGOS NO RASPBERRY PI 5..."

# 1. Atualizar o sistema
sudo apt update && sudo apt upgrade -y

# 2. Instalar dependências de sistema (Áudio e Vídeo)
sudo apt install -y python3-pyaudio libespeak1 python3-opencv i2c-tools

# 3. Habilitar I2C e Câmera (Configuração do Hardware)
# Nota: No Pi 5 a câmera geralmente é automática, mas o I2C precisa ligar
sudo raspi-config nonint do_i2c 0

# 4. Criar ambiente virtual Python (Para não bagunçar o sistema)
python3 -m venv venv
source venv/bin/activate

# 5. Instalar as bibliotecas do nosso projeto
# (O 'requirements.txt' que criamos antes deve estar na mesma pasta)
pip install -r requirements.txt

# 6. Instalar bibliotecas de Hardware Real (Que não instalamos no PC)
pip install adafruit-circuitpython-pca9685 adafruit-circuitpython-servokit
pip install smbus2

# 7. Instalar bibliotecas adicionais necessárias para áudio
sudo apt-get update
sudo apt-get install python3-pyaudio portaudio19-dev espeak

echo "✅ Instalação Concluída! Reinicie o Pi e rode 'python main.py'"