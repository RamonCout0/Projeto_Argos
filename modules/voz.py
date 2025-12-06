import os
import pvporcupine
import pvrecorder
import speech_recognition as sr
import pygame
import time
import subprocess
import pyttsx3 
import config # Importa as configurações do arquivo acima

class VozArgos:
    def __init__(self):
        print("[VOZ] Inicializando subsistema de áudio...")
        
        # 1. Configura Player de Áudio (Pygame)
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=4096)
            pygame.mixer.music.set_volume(config.VOLUME_SISTEMA)
            
            # Carrega sons de feedback (Se existirem)
            self.som_bip = None
            if os.path.exists(config.SOM_BIP):
                self.som_bip = pygame.mixer.Sound(config.SOM_BIP)
                
        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha no Mixer de som: {e}")

        # 2. Configura Backup Offline (Pyttsx3)
        self.engine_offline = pyttsx3.init()
        self.engine_offline.setProperty('rate', 160)

        # 3. Configura Porcupine (Gatilho)
        try:
            self.porcupine = pvporcupine.create(
                access_key=config.PICOVOICE_KEY,
                keywords=[config.WAKE_WORD]
            )
            self.recorder = pvrecorder.PvRecorder(
                device_index=-1, 
                frame_length=self.porcupine.frame_length
            )
            self.recorder.start()
            print(f"[VOZ] Gatilho ativo: '{config.WAKE_WORD}'")
        except Exception as e:
            print(f"[ERRO] Porcupine falhou: {e}")
            self.porcupine = None

        # 4. Configura Ouvido (Speech Recognition)
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = False # Desliga auto-ajuste (Causa bugs)
        self.recognizer.energy_threshold = config.SENSIBILIDADE_MIC
        self.recognizer.pause_threshold = 1.2 # Paciência de silêncio

    def tocar_feedback(self):
        """ Toca um BIP curto """
        if self.som_bip:
            self.som_bip.play()
        else:
            print("[BIP] (Arquivo de som não encontrado)")

    def detectar_wake_word(self):
        """ Verifica gatilho sem bloquear """
        if not self.porcupine: return False
        try:
            pcm = self.recorder.read()
            if self.porcupine.process(pcm) >= 0: return True
        except: pass
        return False

    def ouvir_comando_completo(self):
        """ Escuta o usuário """
        print("--- OUVINDO ---")
        
        # Toca o BIP para avisar que está ouvindo
        self.tocar_feedback()

        if self.recorder.is_recording: self.recorder.stop()
        
        texto = ""
        try:
            with sr.Microphone() as source:
                # Ouve com timeout para não travar
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=15)
                print("--- PROCESSANDO ---")
                texto = self.recognizer.recognize_google(audio, language='pt-BR')
        except sr.WaitTimeoutError:
            print("[VOZ] Silêncio (Timeout).")
        except Exception as e:
            print(f"[VOZ] Não entendi: {e}")
            
        if not self.recorder.is_recording: self.recorder.start()
        return texto

    def falar(self, texto):
        """ Fala usando Edge (Online) ou Pyttsx3 (Offline) """
        if not texto: return
        print(f"[ARGOS]: {texto}")
        
        caminho_arquivo = os.path.abspath("fala_temp.mp3")
        sucesso_online = False

        # TENTATIVA 1: EDGE TTS (Online)
        try:
            if os.path.exists(caminho_arquivo):
                pygame.mixer.music.unload()
                try: os.remove(caminho_arquivo)
                except: pass

            comando = f'edge-tts --text "{texto}" --voice {config.VOZ_NEURAL} --write-media "{caminho_arquivo}"'
            
            # Correção de Encoding para Windows
            subprocess.run(comando, shell=True, check=True, encoding='utf-8', errors='ignore', capture_output=True)
            
            if os.path.exists(caminho_arquivo) and os.path.getsize(caminho_arquivo) > 0:
                pygame.mixer.music.load(caminho_arquivo)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                pygame.mixer.music.unload()
                sucesso_online = True

        except Exception as e:
            print(f"[AVISO] Falha voz neural: {e}")

        # TENTATIVA 2: BACKUP (Offline)
        if not sucesso_online:
            try:
                self.engine_offline.say(texto)
                self.engine_offline.runAndWait()
            except: pass

    def __del__(self):
        if self.porcupine: self.porcupine.delete()
        if self.recorder: self.recorder.delete()