import os
import pvporcupine
import pvrecorder
import speech_recognition as sr
import pygame
import time
import subprocess
import pyttsx3 

# --- CONFIGURAÇÕES ---
PICOVOICE_ACCESS_KEY = "censurado" 
VOZ_EDGE = "pt-BR-AntonioNeural"

class VozArgos:
    def __init__(self):
        print("[VOZ] Inicializando subsistema de áudio...")
        
        # 1. Configura Pygame (Player) com frequência padrão segura
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            pygame.mixer.music.set_volume(1.0)
        except Exception as e:
            print(f"[ERRO CRÍTICO] Pygame Mixer falhou: {e}")

        # 2. Configura Backup Offline
        self.engine_offline = pyttsx3.init()
        self.engine_offline.setProperty('rate', 160)

        # 3. Configura Porcupine
        try:
            self.porcupine = pvporcupine.create(
                access_key=PICOVOICE_ACCESS_KEY,
                keywords=['jarvis']
            )
            self.recorder = pvrecorder.PvRecorder(
                device_index=-1, 
                frame_length=self.porcupine.frame_length
            )
            self.recorder.start()
        except Exception as e:
            print(f"[ERRO] Porcupine falhou (Verifique a chave): {e}")
            self.porcupine = None

        # 4. Configura Ouvido (Sensibilidade Fixa)
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = False
        self.recognizer.energy_threshold = 400
        self.recognizer.pause_threshold = 1.0

    def detectar_wake_word(self):
        if not self.porcupine: return False
        try:
            pcm = self.recorder.read()
            if self.porcupine.process(pcm) >= 0: return True
        except: pass
        return False

    def ouvir_comando_completo(self):
        print("--- OUVINDO (Pode falar à vontade...) ---")
        
        # Solta o microfone do Porcupine
        if self.recorder.is_recording:
            self.recorder.stop()
        
        texto_reconhecido = ""
        
        try:
            with sr.Microphone() as source:
                # Dica: Ajuste este valor se ele demorar muito para 'perceber' que você parou
                self.recognizer.pause_threshold = 2.0  # Espera 2s de silêncio antes de finalizar
                
                # Ajuste rápido do ruído antes de começar
                # self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # O SEGREDO ESTÁ AQUI:
                # timeout=5 -> Espera até 5s para você COMEÇAR a falar
                # phrase_time_limit=None -> Não tem limite de tempo para a frase!
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=None)
                
                print("--- PROCESSANDO ---")
                texto_reconhecido = self.recognizer.recognize_google(audio, language='pt-BR')
                
        except sr.WaitTimeoutError:
            print("[VOZ] Silêncio detectado (Timeout).")
        except sr.UnknownValueError:
            print("[VOZ] Não entendi (Áudio confuso).")
        except Exception as e:
            print(f"[VOZ] Erro técnico: {e}")
            
        # Retoma o Porcupine
        if not self.recorder.is_recording:
            self.recorder.start()
            
        return texto_reconhecido

    def falar(self, texto):
        if not texto: return
        print(f"[ARGOS TENTA FALAR]: {texto}")
        
        # Define caminho absoluto para evitar erros de pasta
        caminho_arquivo = os.path.abspath("fala_temp.mp3")
        sucesso_online = False

        # --- TENTATIVA 1: EDGE TTS (Online) ---
        try:
            # 1. Limpeza
            if os.path.exists(caminho_arquivo):
                pygame.mixer.music.unload() # Solta o arquivo
                try: os.remove(caminho_arquivo)
                except: pass

            # 2. Geração do Áudio
            print(" -> Gerando MP3...")
            comando = f'edge-tts --text "{texto}" --voice {VOZ_EDGE} --write-media "{caminho_arquivo}"'
            
            # Executa e captura erro se houver
            resultado = subprocess.run(
                comando, 
                shell=True, 
                capture_output=True, 
                text=True, 
                encoding='utf-8',  # <--- O SEGREDO ESTÁ AQUI
                errors='ignore'    # <--- IGNORA CARACTERES ESTRANHOS
            )
            
            if resultado.returncode != 0:
                print(f"[ERRO EDGE] Falha no comando: {resultado.stderr}")
                raise Exception("Comando falhou")

            # 3. Reprodução
            if os.path.exists(caminho_arquivo) and os.path.getsize(caminho_arquivo) > 0:
                print(" -> Tocando áudio...")
                pygame.mixer.music.load(caminho_arquivo)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                pygame.mixer.music.unload()
                sucesso_online = True
            else:
                print("[ERRO EDGE] Arquivo MP3 não foi criado ou está vazio.")

        except Exception as e:
            print(f"[AVISO] Falha na voz Neural: {e}")

        # --- TENTATIVA 2: BACKUP (Offline) ---
        if not sucesso_online:
            print(" -> Usando voz de backup (Offline)...")
            try:
                self.engine_offline.say(texto)
                self.engine_offline.runAndWait()
            except Exception as e:
                print(f"[ERRO TOTAL] Nem o backup funcionou: {e}")

    def __del__(self):
        if self.porcupine: self.porcupine.delete()
        if self.recorder: self.recorder.delete()