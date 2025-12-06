import cv2
import os
import config 

class OlhosArgos:
    def __init__(self):
        print("[VISAO] Inicializando com Buffer Gráfico...")
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        
        # Configura resolução
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.RESOLUCAO_CAM[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.RESOLUCAO_CAM[1])
        
        # Carrega IA
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        self.modelo_carregado = False
        if os.path.exists("treinador_argos.yml"):
            try:
                self.recognizer.read("treinador_argos.yml")
                self.modelo_carregado = True
                print("[VISAO] Cérebro visual carregado.")
            except:
                print("[VISAO] Erro no arquivo de treino.")
        else:
            print("[VISAO] ALERTA: Rode 'cadastrar_dono.py' para ser reconhecido!")

        # Variáveis de Otimização
        self.frame_count = 0 
        # Cache guarda: (detectado, x, y, identidade, coordenadas_do_retangulo)
        self.cache_resultado = (False, 0, 0, "DESCONHECIDO", None) 

    def ver(self):
        ret, frame = self.cap.read()
        if not ret: return False, 0, 0, "DESCONHECIDO"

        self.frame_count += 1
        
        # --- LÓGICA DE CÁLCULO (Roda a cada X frames) ---
        if self.frame_count % config.FRAME_SKIP == 0:
            
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)
            
            if len(faces) > 0:
                # Pega o primeiro rosto
                (x, y, w, h) = faces[0]
                
                identidade = "DESCONHECIDO"
                
                # Reconhecimento
                if self.modelo_carregado:
                    id_predito, confianca = self.recognizer.predict(gray[y:y+h, x:x+w])
                    # Confiança menor é melhor (0 = perfeito)
                    if confianca < 65: 
                        identidade = "DONO"
                    else:
                        identidade = "DESCONHECIDO"
                
                # Cálculos de centro
                centro_x = x + w // 2
                centro_y = y + h // 2
                height, width, _ = frame.shape
                erro_x = centro_x - (width // 2)
                erro_y = centro_y - (height // 2)

                # Atualiza o Cache
                self.cache_resultado = (True, erro_x, erro_y, identidade, (x, y, w, h))
            else:
                # Ninguém na tela
                self.cache_resultado = (False, 0, 0, "DESCONHECIDO", None)

        # --- LÓGICA DE DESENHO (Roda SEMPRE, usando o Cache) ---
        # Desempacota as variáveis do cache
        detectado, erro_x, erro_y, identidade, rect = self.cache_resultado
        
        if detectado and rect is not None:
            (x, y, w, h) = rect
            
            # CORREÇÃO AQUI: Usando 'identidade' em vez de 'identity'
            if identidade == "DONO":
                cor = (0, 255, 0) # Verde
                texto = f"DONO"
            else:
                cor = (0, 0, 255) # Vermelho
                texto = "INTRUSO"
            
            # Desenha usando os dados do cache
            cv2.rectangle(frame, (x, y), (x+w, y+h), cor, 2)
            cv2.putText(frame, texto, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, cor, 2)

        # Mostra a janela (Se estiver no modo Simulação/Windows)
        if config.SIMULACAO:
            cv2.imshow("Visao Argos", frame)
            if cv2.waitKey(1) == ord('q'): pass

        return detectado, erro_x, erro_y, identidade