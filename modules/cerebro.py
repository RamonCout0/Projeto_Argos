import ollama
import chromadb
from datetime import datetime
import json
import requests

try:
    from modules.ferramentas import buscar_agenda, tocar_spotify
except ImportError:
    pass



class CerebroArgos:
    def __init__(self):
        print("[CEREBRO] Inicializando memória e modelos...")
        # self.memoria = chromadb.Client() ... (configuração do Chroma)
        self.modo_offline = False

    def verificar_conexao(self):
        """Testa se tem internet real"""
        try:
            requests.get("https://www.google.com", timeout=1.5)
            return True
        except:
            return False

    def processar_comando(self, texto_usuario):
        """
        Recebe o texto e decide:
        1. É comando de hardware? (Dançar, Parar) -> Retorna ação
        2. É ferramenta? (Agenda, Música) -> Executa API
        3. É conversa? -> Gera resposta (LLM)
        """
        texto = texto_usuario.lower()
        self.modo_online = self.verificar_conexao()

        # --- CAMADA 1: Roteador Rápido (Regex/Palavras-chave) ---
        
        # Comandos Físicos (Para modules/movimento.py executar)
        if "dançar" in texto:
            return {"tipo": "movimento", "acao": "dancar", "resposta": "Vamos dançar!"}
        
        if "parar" in texto:
            return {"tipo": "movimento", "acao": "parar", "resposta": "Parando agora."}

        # Comandos de Ferramentas
        if "agenda" in texto and self.modo_online:
            # resposta_agenda = buscar_agenda()
            return {"tipo": "fala", "resposta": "Verificando sua agenda..."}
            
        # --- CAMADA 2: Inteligência (Conversa) ---
        
        # 1. Recuperar contexto da memória (RAG)
        # contexto = self.memoria.query(texto)...
        
        if self.modo_online:
            print("[CEREBRO] Modo Online: Usando IA Avançada (GPT/Gemini)...")
            # resposta = chamar_api_gpt(texto, contexto)
            resposta = "Resposta simulada da Nuvem."
        else:
            print("[CEREBRO] Modo Offline: Usando Ollama (Llama 3)...")
            # resposta = ollama.chat(model='llama3', messages=[...])
            resposta = "Estou sem internet, mas lembro que conversamos sobre isso."

        # 2. Salvar nova memória no ChromaDB aqui
        
        return {"tipo": "fala", "resposta": resposta}