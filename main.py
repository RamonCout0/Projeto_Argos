import threading
import time
import keyboard
import config # Suas configurações novas
from modules.cerebro import CerebroArgos
from modules.movimento import HexapodDriver
from modules.visao import OlhosArgos
from modules.voz import VozArgos

# --- VARIÁVEIS GLOBAIS ---
dados_visao = {"detectado": False, "x": 0, "y": 0, "quem": "DESCONHECIDO"}
estado_sistema = {"ativo": True, "rastreio": True, "ouvindo": False}

# --- THREAD: SUBCONSCIENTE VISUAL ---
def subconsciente_motor(argos_eyes, argos_legs):
    print("   [THREAD] Visão Biométrica iniciada.")
    while estado_sistema["ativo"]:
        if estado_sistema["rastreio"]:
            # A visão usa o config.FRAME_SKIP internamente no visao.py
            detectado, erro_x, erro_y, identidade = argos_eyes.ver()
            
            dados_visao["detectado"] = detectado
            dados_visao["x"] = erro_x
            dados_visao["y"] = erro_y
            dados_visao["quem"] = identidade 

            # Só mexe se detectar rosto e não estiver gravando áudio (silêncio mecânico)
            if detectado and not estado_sistema["ouvindo"]:
                argos_legs.atualizar_rastreio(erro_x, erro_y)
                
        time.sleep(0.01)

# --- THREAD: CONSCIENTE (PRINCIPAL) ---
def main():
    print("===================================")
    print("      ARGOS v9 - OTIMIZADO         ")
    print("===================================")

    # Inicializa Módulos
    argos_brain = CerebroArgos()
    argos_legs = HexapodDriver(simulacao=config.SIMULACAO) 
    argos_eyes = OlhosArgos()
    argos_voice = VozArgos()

    # Inicia Visão em Paralelo
    thread_visao = threading.Thread(target=subconsciente_motor, args=(argos_eyes, argos_legs))
    thread_visao.daemon = True
    thread_visao.start()

    argos_voice.falar("Sistemas online e operantes.")
    print("\n✅ Modo Sentinela Ativo. Pressione ESC para sair.")

    while estado_sistema["ativo"]:
        
        # 1. VERIFICA GATILHO (Rápido e leve)
        if argos_voice.detectar_wake_word():
            print("\n[!] Solicitado!")
            
            # Pausa motores para diminuir ruído
            estado_sistema["ouvindo"] = True 
            time.sleep(0.3) 
            
            # Ouve (O Bip é tocado dentro desta função agora)
            comando = argos_voice.ouvir_comando_completo()
            
            # Libera motores
            estado_sistema["ouvindo"] = False 
            
            if comando:
                print(f"Comando reconhecido: {comando}")
                
                # --- LÓGICA DE SEGURANÇA ---
                quem = dados_visao["quem"]
                resultado = None

                if quem == "DONO":
                    resultado = argos_brain.processar_comando(comando)
                
                elif quem == "DESCONHECIDO":
                    if any(x in comando.lower() for x in ["quem sou", "senha", "agenda", "dinheiro"]):
                        resultado = {"tipo": "fala", "resposta": "Acesso negado. Biometria inválida."}
                    else:
                        resultado = argos_brain.processar_comando(comando)
                
                else: # Ninguém na tela
                    resultado = argos_brain.processar_comando(comando)

                # --- EXECUÇÃO ---
                if resultado:
                    if resultado['tipo'] == 'fala':
                        texto = resultado['resposta']
                        argos_voice.falar(texto)
                        
                        # OTIMIZAÇÃO: Se abriu navegador (Youtube/Google), espera um pouco
                        if "Abrindo" in texto or "Pesquisando" in texto or "Tocando" in texto:
                            print("[SISTEMA] Pausa para carregamento da janela...")
                            time.sleep(3.5) # Tempo para o vídeo começar e não gerar loop de áudio

                    elif resultado['tipo'] == 'movimento':
                        argos_voice.falar(resultado['resposta'])
                        acao = resultado['acao']
                        if acao == 'parar': estado_sistema["rastreio"] = False
                        # elif acao == 'dancar': argos_legs.dancar()

        # Saída
        if keyboard.is_pressed('esc'):
            print("Desligando...")
            estado_sistema["ativo"] = False
            break
            
        time.sleep(0.05)

    thread_visao.join()

if __name__ == "__main__":
    main()