import webbrowser
import threading
import time
import pywhatkit # <--- Trazemos ele de volta

def _acao_background(intencao, parametro):
    """ Roda em segundo plano para o robô não travar """
    try:
        if intencao == "tocar_musica":
            # O pywhatkit escolhe o melhor vídeo e dá Play sozinho
            print(f"[YOUTUBE] Tocando: {parametro}")
            pywhatkit.playonyt(parametro)
            
        elif intencao == "url_direta":
            # Para pesquisas e agenda, usa o método rápido
            webbrowser.open(parametro)
            
    except Exception as e:
        print(f"[ERRO BACKGROUND]: {e}")

def executar_ferramenta(intencao, parametro):
    """ Gerencia qual ferramenta usar """
    print(f"[FERRAMENTA] Ação: {intencao} | Alvo: {parametro}")
    
    feedback = ""
    thread_alvo = None

    # --- 1. MÚSICA (Usa PyWhatKit para Autoplay) ---
    if intencao == "tocar_musica":
        feedback = f"Tocando {parametro} no YouTube."
        # Cria thread chamando a função pesada
        thread_alvo = threading.Thread(target=_acao_background, args=("tocar_musica", parametro))

    # --- 2. PESQUISA (Usa URL Direta - Mais Rápido) ---
    elif intencao == "pesquisar_web":
        termo = parametro.replace(" ", "+")
        url = f"https://www.google.com/search?q={termo}"
        feedback = f"Pesquisando sobre {parametro}."
        thread_alvo = threading.Thread(target=_acao_background, args=("url_direta", url))

    # --- 3. AGENDA ---
    elif intencao == "abrir_agenda":
        feedback = "Abrindo sua agenda."
        thread_alvo = threading.Thread(target=_acao_background, args=("url_direta", "https://calendar.google.com/calendar/r"))

    # --- 4. NOTÍCIAS ---
    elif intencao == "noticias":
        feedback = "Abrindo notícias."
        thread_alvo = threading.Thread(target=_acao_background, args=("url_direta", "https://news.google.com/"))

    # Inicia a ação sem bloquear o robô
    if thread_alvo:
        thread_alvo.start()
        return feedback

    return "Ferramenta desconhecida."