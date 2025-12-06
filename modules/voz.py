import pvporcupine
import pvrecorder
import speech_recognition as sr
import os
import platform
import subprocess

# COLOQUE SUA CHAVE DO PICOVOICE AQUI
PICOVOICE_ACCESS_KEY = "acessonebetinha"

class VozArgos:
    def __init__(self):
        print("[VOZ] Inicializando sistema de audição...")
        
        # 1. Configuração do Porcupine (Gatilho)
        # keywords pode ser 'jarvis', 'computer', 'alexa', 'hey siri' (padrões)
        # Para criar "Ei Argos", você precisa treinar no site deles ou usar 'jarvis' por enquanto.
        try:
            self.porcupine = pvporcupine.create(
                access_key=PICOVOICE_ACCESS_KEY,
                keywords=['jarvis'] # Vamos usar 'Jarvis' como teste, depois mudamos
            )
            self.recorder = pvrecorder.PvRecorder(
                device_index=-1, 
                frame_length=self.porcupine.frame_length
            )
            self.recorder.start()
            print(f"[VOZ] Escutando gatilho 'Jarvis'...")
        except Exception as e:
            print(f"[ERRO] Falha ao iniciar Porcupine: {e}")
            self.porcupine = None

        # 2. Configuração do Reconhecimento de Fala (Comando Completo)
        self.recognizer = sr.Recognizer()
        
        # Ajuste para melhorar precisão em ambiente com ruído de motor
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

    def detectar_wake_word(self):
        """
        Lê apenas um frame de áudio (milissegundos).
        Retorna True se ouviu a palavra chave.
        NÃO BLOQUEIA O LOOP.
        """
        if not self.porcupine:
            return False

        try:
            pcm = self.recorder.read()
            result = self.porcupine.process(pcm)
            
            if result >= 0:
                print("[VOZ] Wake Word detectada!")
                return True
        except Exception as e:
            print(f"[ERRO] Leitura de áudio: {e}")
            
        return False

    def ouvir_comando_completo(self):
        """
        Pausa o detector de gatilho e grava a frase inteira.
        Usa o Google STT (Online) ou Whisper (Offline) para converter.
        """
        print("[VOZ] Gravando comando...")
        
        # IMPORTANTE: Parar o recorder do Porcupine para liberar o mic
        self.recorder.stop()
        
        texto_reconhecido = ""
        
        try:
            with sr.Microphone() as source:
                # Calibração rápida de ruído
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Ouve (com timeout para não travar se ninguem falar)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                
                print("[VOZ] Processando áudio...")
                # Opção A: Google (Rápido, precisa de net)
                # texto_reconhecido = self.recognizer.recognize_google(audio, language='pt-BR')
                
                # Opção B: Whisper Local (Offline - Ideal para o Pi 5)
                # Requer que você tenha instalado o whisper
                # Por enquanto vamos de Google para testar:
                texto_reconhecido = self.recognizer.recognize_google(audio, language='pt-BR')
                
        except sr.WaitTimeoutError:
            print("[VOZ] Tempo esgotado. Ninguém falou.")
        except sr.UnknownValueError:
            print("[VOZ] Não entendi o áudio.")
        except Exception as e:
            print(f"[VOZ] Erro: {e}")
        
        # IMPORTANTE: Reiniciar o recorder do Porcupine para a próxima vez
        self.recorder.start()
        
        return texto_reconhecido

    def falar(self, texto):
        """
        Sintetiza voz. 
        No Pi 5, use 'piper' (offline) ou 'espeak'.
        """
        print(f"[ROBÔ]: {texto}")
        
        # Exemplo simples com espeak (robótico, mas funciona na hora)
        # Instale com: sudo apt install espeak
        comando = f'espeak -v pt-br "{texto}"'
        
        # Se você já tiver o Piper configurado:
        # comando = f'echo "{texto}" | ./piper --model pt_BR-fabio-medium.onnx --output_file tocando.wav && aplay tocando.wav'
        
        os.system(comando)