from modules.cerebro import CerebroArgos
from modules.movimento import HexapodDriver
from modules.visao import OlhosArgos
from modules.voz import VozArgos
import time
import keyboard

def main():
    print("===================================")
    print("      INICIALIZANDO ARGOS v5       ")
    print("      (Cognitivo + Sentinela)      ")
    print("===================================")

    # 1. Inicializa os subsistemas
    argos_brain = CerebroArgos()
    argos_legs = HexapodDriver(simulacao=True) # Mude para False no robô real
    argos_eyes = OlhosArgos()
    argos_voice = VozArgos()

    # Estado inicial
    modo_rastreio = True
    argos_voice.falar("Sistemas online. Modo sentinela ativo.")
    
    print("\n✅ Loop Principal Iniciado. Pressione ESC para sair.")

    while True:
        # --- BLOCO 1: VISÃO & RASTREIO ---
        if modo_rastreio:
            detectado, erro_x, erro_y = argos_eyes.ver()
            if detectado:
                argos_legs.atualizar_rastreio(erro_x, erro_y)

        # --- BLOCO 2: AUDIÇÃO (O GATILHO) ---
        # ### NOVO: Verifica se chamou o nome "Argos" sem travar o vídeo
        # Essa função deve ser muito rápida (retorna False se ninguém falar)
        if argos_voice.detectar_wake_word(): 
            print("\n[!] Gatilho detectado! Ouvindo comando...")
            
            # 1. Feedback visual/sonoro
            argos_voice.falar("Sim?") 
            
            # 2. Ouve o comando completo (Aqui ele pode parar o vídeo rapidinho)
            comando_texto = argos_voice.ouvir_comando_completo()
            
            if comando_texto:
                print(f"Você disse: {comando_texto}")
                
                # 3. Manda para o Cérebro Híbrido (Ollama/GPT)
                resultado = argos_brain.processar_comando(comando_texto)
                
                # 4. Executa a decisão do Cérebro
                tipo_acao = resultado['tipo'] # 'fala', 'movimento', 'ferramenta'
                conteudo = resultado['resposta']
                
                # Se for fala, ele responde
                if conteudo:
                    argos_voice.falar(conteudo)

                # Se for movimento físico (Ex: "Dançar", "Sentar")
                if tipo_acao == 'movimento':
                    acao_fisica = resultado.get('acao')
                    if acao_fisica == 'parar':
                        modo_rastreio = False # Para de seguir o rosto
                    elif acao_fisica == 'rastrear':
                        modo_rastreio = True
                    else:
                        # Executa movimentos complexos (danca, etc)
                        argos_legs.executar_script(acao_fisica)

        # --- SAÍDA ---
        if keyboard.is_pressed('esc'):
            print("\nDesligando...")
            break
            
        # Pequena pausa para respirar a CPU
        # time.sleep(0.01)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nFinalizando via Terminal.")