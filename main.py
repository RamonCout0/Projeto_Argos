import threading
import time
import keyboard
from modules.cerebro import CerebroArgos
from modules.movimento import HexapodDriver
from modules.visao import OlhosArgos
from modules.voz import VozArgos

# --- VARIÁVEIS GLOBAIS ---
# Adicionamos "quem" para saber a identidade da pessoa
dados_visao = {"detectado": False, "x": 0, "y": 0, "quem": "DESCONHECIDO"}
estado_sistema = {"ativo": True, "rastreio": True, "ouvindo": False}

# --- THREAD 1: O SUBCONSCIENTE (Visão e Motor) ---
def subconsciente_motor(argos_eyes, argos_legs):
    print("   [THREAD] Visão Biométrica iniciada.")
    
    while estado_sistema["ativo"]:
        if estado_sistema["rastreio"]:
            # 1. VISÃO: Obtém dados (Agora inclui a IDENTIDADE)
            detectado, erro_x, erro_y, identidade = argos_eyes.ver()
            
            # Atualiza variáveis globais para a Thread Principal ler
            dados_visao["detectado"] = detectado
            dados_visao["x"] = erro_x
            dados_visao["y"] = erro_y
            dados_visao["quem"] = identidade 

            # 2. MOVIMENTO: Só move se não estiver ouvindo (para reduzir ruído)
            if detectado and not estado_sistema["ouvindo"]:
                argos_legs.atualizar_rastreio(erro_x, erro_y)
            
        time.sleep(0.01)

# --- THREAD 2: O CONSCIENTE (Cérebro e Voz) ---
def main():
    print("===================================")
    print("      ARGOS v7 - SENTINELA         ")
    print("===================================")

    argos_brain = CerebroArgos()
    argos_legs = HexapodDriver(simulacao=True) 
    argos_eyes = OlhosArgos()
    argos_voice = VozArgos()

    # Inicia a visão em paralelo
    thread_visao = threading.Thread(target=subconsciente_motor, args=(argos_eyes, argos_legs))
    thread_visao.daemon = True
    thread_visao.start()

    argos_voice.falar("Sistemas de segurança ativos.")
    print("\n✅ Modo Sentinela. Pressione ESC para sair.")

    while estado_sistema["ativo"]:
        
        # 1. GATILHO (Wake Word)
        if argos_voice.detectar_wake_word():
            print("\n[!] Solicitado! Verificando ambiente...")
            
            estado_sistema["ouvindo"] = True 
            time.sleep(0.5) 
            
            argos_voice.falar("Sim?")
            comando = argos_voice.ouvir_comando_completo()
            
            estado_sistema["ouvindo"] = False 
            
            if comando:
                print(f"Comando: {comando}")
                
                # --- AQUI ENTRA O BLOCO DE SEGURANÇA QUE VOCÊ PERGUNTOU ---
                
                quem_esta_na_frente = dados_visao["quem"]
                print(f"[SEGURANÇA] Identificado visualmente: {quem_esta_na_frente}")

                resultado = None

                # CENÁRIO 1: É o Dono (Acesso Total)
                if quem_esta_na_frente == "DONO":
                    resultado = argos_brain.processar_comando(comando)
                
                # CENÁRIO 2: Desconhecido (Acesso Restrito)
                elif quem_esta_na_frente == "DESCONHECIDO":
                    # Se perguntar dados sensíveis, nega.
                    if "quem sou eu" in comando.lower() or "senha" in comando.lower() or "agenda" in comando.lower():
                        resultado = {"tipo": "fala", "resposta": "Acesso negado. Identidade não confirmada."}
                    else:
                        # Se for conversa fiada ou horas, ele responde normal
                        resultado = argos_brain.processar_comando(comando) 

                # CENÁRIO 3: Ninguém na câmera (Fantasma?)
                else:
                     # Se ele ouviu voz mas não vê ninguém, pode responder, mas com cautela
                    resultado = argos_brain.processar_comando(comando)
                    # Opcional: resultado = {"tipo": "fala", "resposta": "Não vejo ninguém aqui."}

                # --- FIM DO BLOCO DE SEGURANÇA ---

                # Executa a ação decidida acima
                if resultado:
                    if resultado['tipo'] == 'movimento':
                        argos_voice.falar(resultado['resposta'])
                        acao = resultado['acao']
                        if acao == 'parar': estado_sistema["rastreio"] = False
                        elif acao == 'dancar': pass 
                        
                    elif resultado['tipo'] == 'fala':
                        argos_voice.falar(resultado['resposta'])

        if keyboard.is_pressed('esc'):
            estado_sistema["ativo"] = False
            break
            
        time.sleep(0.05)

    thread_visao.join()

if __name__ == "__main__":
    main()