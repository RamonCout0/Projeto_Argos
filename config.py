# config.py
import os

# --- IDENTIDADE & SEGURANÇA ---
NOME_ROBO = "Argos"
WAKE_WORD = "jarvis" # Ou o nome do seu arquivo .ppn
PICOVOICE_KEY = "censurado ne betinha" 

# --- HARDWARE & VISÃO ---
SIMULACAO = True         # True = Windows (abre janelas), False = Raspberry Pi (Headless)
FRAME_SKIP = 3           # Processa visão a cada 3 frames (Economiza CPU)
RESOLUCAO_CAM = (320, 240) # <--- CORRIGIDO: O nome agora bate com o erro

# --- ÁUDIO ---
VOZ_NEURAL = "pt-BR-AntonioNeural" # Ou "pt-BR-FranciscaNeural"
SENSIBILIDADE_MIC = 400  # 300 (Silencioso) a 800 (Barulhento)
VOLUME_SISTEMA = 1.0

# --- ARQUIVOS DE SOM ---
# Se você usou o script gerador, use .wav
# Se baixou da internet, provavelmente é .mp3
SOM_BIP = "bip_ouvir.wav" 
SOM_ERRO = "bip_erro.wav"