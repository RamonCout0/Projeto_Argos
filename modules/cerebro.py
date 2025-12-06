import ollama
import chromadb
import datetime
import uuid
from modules.ferramentas import executar_ferramenta

# --- CONFIGURAÇÃO ---
PERSONALIDADE = """
Você é o ARGOS. Responda de forma curta, leal e técnica.
Você tem acesso a ferramentas: se o usuário pedir música, pesquisa ou agenda, avise que vai executar.
"""

def limpar_texto(texto, gatilhos):
    """ Remove palavras como 'tocar', 'por favor', 'o que é' para sobrar só o assunto """
    lixo = ["por favor", "poderia", "gostaria de", "argos", "ei ", "olá", "me mostre"]
    texto_limpo = texto
    
    # Remove gatilhos (ex: remove 'tocar' de 'tocar rock')
    for g in gatilhos:
        texto_limpo = texto_limpo.replace(g, "")
        
    # Remove lixo
    for l in lixo:
        texto_limpo = texto_limpo.replace(l, "")
        
    return texto_limpo.strip()

class CerebroArgos:
    def __init__(self):
        print("[CEREBRO] Núcleo Otimizado v2.")
        try:
            self.client_db = chromadb.PersistentClient(path="./memoria_argos")
            self.collection = self.client_db.get_or_create_collection(name="conversas_argos")
        except:
            self.collection = None

    def processar_comando(self, texto_usuario):
        texto_raw = texto_usuario.lower()
        
        # --- CAMADA 1: FERRAMENTAS E AÇÕES RÁPIDAS (Prioridade) ---
        
        # Música
        gatilhos_musica = ["tocar", "ouvir", "bota um", "toque"]
        if any(g in texto_raw for g in gatilhos_musica):
            busca = limpar_texto(texto_raw, gatilhos_musica)
            if busca: # Só executa se tiver algo para buscar
                resp = executar_ferramenta("tocar_musica", busca)
                return {"tipo": "fala", "resposta": resp}

        # Pesquisa
        gatilhos_pesquisa = ["pesquisar", "pesquise", "procurar", "quem é", "o que é", "me fale sobre"]
        if any(g in texto_raw for g in gatilhos_pesquisa):
            busca = limpar_texto(texto_raw, gatilhos_pesquisa)
            if busca:
                resp = executar_ferramenta("pesquisar_web", busca)
                return {"tipo": "fala", "resposta": resp}

        # Agenda e Notícias
        if "agenda" in texto_raw or "compromissos" in texto_raw:
            return {"tipo": "fala", "resposta": executar_ferramenta("abrir_agenda", "")}
        
        if "notícias" in texto_raw or "jornal" in texto_raw:
            return {"tipo": "fala", "resposta": executar_ferramenta("noticias", "")}

        # Comandos Físicos
        if "dançar" in texto_raw:
            return {"tipo": "movimento", "acao": "dancar", "resposta": "Executando dança."}
        if "parar" in texto_raw:
            return {"tipo": "movimento", "acao": "parar", "resposta": "Motores parados."}

        # --- CAMADA 2: MEMÓRIA E INTELIGÊNCIA (LLM) ---
        # Se chegou aqui, não é ferramenta, é conversa.
        print("[CEREBRO] Processando conversa...")
        
        # Recupera memória (RAG)
        contexto_memoria = ""
        if self.collection:
            res = self.collection.query(query_texts=[texto_raw], n_results=1)
            if res['documents'][0]:
                contexto_memoria = res['documents'][0][0]

        # Gera resposta com Llama
        prompt = f"{PERSONALIDADE}\nMemória: {contexto_memoria}\nUsuário: {texto_usuario}"
        
        try:
            response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
            resposta_ia = response['message']['content']
            
            # Salva na memória
            if self.collection:
                self.collection.add(
                    documents=[f"User: {texto_usuario} | Bot: {resposta_ia}"],
                    ids=[str(uuid.uuid4())]
                )
        except:
            resposta_ia = "Estou desconectado do meu núcleo neural."

        return {"tipo": "fala", "resposta": resposta_ia}