import ollama
import chromadb
import datetime
import uuid # Para gerar IDs únicos para as memórias

# --- CONFIGURAÇÃO DA PERSONALIDADE ---
# Aqui você define a "Alma" do robô.
PERSONALIDADE = """
Você é o ARGOS (Autonomous Robotic Guardian & Observation System), versão 6.0.
SUA MISSÃO: Ser um assistente físico útil, leal e protetor.

DIRETRIZES DE COMPORTAMENTO:
1. Seja objetivo e direto. Não faça discursos longos.
2. Tenha um tom levemente técnico, mas amigável.
3. Você tem corpo físico. Se pedirem para "andar" ou "olhar", diga que está ativando os servos.
4. Se perguntarem quem é você, diga que é um robô hexápode desenvolvido pelo seu Criador.
5. Use o contexto das memórias passadas para personalizar a conversa.
"""

class CerebroArgos:
    def __init__(self):
        print("[CEREBRO] Inicializando Núcleo Cognitivo...")
        
        # 1. Conexão com a Memória (ChromaDB)
        # O caminho ./memoria_argos deve ser o mesmo que vi no seu print
        try:
            self.client_db = chromadb.PersistentClient(path="./memoria_argos")
            self.collection = self.client_db.get_or_create_collection(name="conversas_argos")
            print(f"[CEREBRO] Memória carregada. Total de lembranças: {self.collection.count()}")
        except Exception as e:
            print(f"[ERRO CEREBRO] Falha ao carregar memória: {e}")
            self.collection = None

    def lembrar(self, texto_busca):
        """ Busca no banco de dados conversas passadas parecidas """
        if not self.collection: return ""
        
        try:
            # Busca as 2 memórias mais relevantes
            resultados = self.collection.query(
                query_texts=[texto_busca],
                n_results=2
            )
            
            # Formata para texto
            memoria_recuperada = ""
            if resultados['documents']:
                lista_docs = resultados['documents'][0]
                memoria_recuperada = "\n".join(lista_docs)
                
            return memoria_recuperada
        except:
            return ""

    def memorizar(self, usuario_disse, bot_disse):
        """ Salva a interação para o futuro """
        if not self.collection: return

        # Formato: "User: texto | Bot: texto"
        conteudo = f"Usuário: {usuario_disse} | Argos: {bot_disse}"
        
        # Salva no banco
        self.collection.add(
            documents=[conteudo],
            ids=[str(uuid.uuid4())], # ID único
            metadatas=[{"data": str(datetime.datetime.now())}]
        )
        print("[CEREBRO] Memória salva.")

    def processar_comando(self, texto_usuario):
        texto = texto_usuario.lower()
        
        # --- COMANDOS RÁPIDOS (Reflexos) ---
        if "dançar" in texto:
            return {"tipo": "movimento", "acao": "dancar", "resposta": "Iniciando protocolo de dança. Observe."}
        if "parar" in texto:
            return {"tipo": "movimento", "acao": "parar", "resposta": "Motores parados. Aguardando."}
        
        # --- RACIOCÍNIO PROFUNDO (LLM + RAG) ---
        print("[CEREBRO] Consultando memória e gerando resposta...")
        
        # 1. Recupera o contexto (O que ele já sabe sobre isso?)
        memoria = self.lembrar(texto_usuario)
        if memoria:
            print(f"   -> Lembrei de: {memoria[:50]}...") # Log curto
        
        # 2. Dados de Tempo Real
        agora = datetime.datetime.now().strftime("%d/%m/%Y às %H:%M")
        
        # 3. Monta o Prompt para o Ollama
        prompt_sistema = f"""
        {PERSONALIDADE}
        DATA ATUAL: {agora}
        
        MEMÓRIAS RELEVANTES (O que você lembra sobre isso):
        {memoria}
        
        Instrução: Use as memórias acima se ajudarem a responder a pergunta atual.
        """

        try:
            # Chama o Llama 3.2
            response = ollama.chat(model='llama3.2', messages=[
                {'role': 'system', 'content': prompt_sistema},
                {'role': 'user', 'content': texto_usuario},
            ])
            resposta_ia = response['message']['content']
            
            # 4. Salva o aprendizado (Evolução)
            self.memorizar(texto_usuario, resposta_ia)
            
        except Exception as e:
            resposta_ia = "Estou com dificuldades de processamento. Verifique meu servidor Ollama."
            print(f"[ERRO LLM]: {e}")

        return {"tipo": "fala", "resposta": resposta_ia}