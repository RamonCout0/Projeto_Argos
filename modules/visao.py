import cv2
import os

class OlhosArgos:
    def __init__(self):
        print("[VISAO] Inicializando sistema LBPH (Leve)...")
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW) 
        
        # Carrega o detector facial (Cascade)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # Carrega o reconhecedor treinado
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.modelo_carregado = False
        
        if os.path.exists("treinador_argos.yml"):
            try:
                self.recognizer.read("treinador_argos.yml")
                self.modelo_carregado = True
                print("[VISAO] Biometria carregada com sucesso.")
            except:
                print("[VISAO] Erro ao ler arquivo de treino.")
        else:
            print("[VISAO] ALERTA: Rode 'cadastrar_dono.py' primeiro!")

    def ver(self):
        ret, frame = self.cap.read()
        if not ret: return False, 0, 0, "DESCONHECIDO"

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, 1.2, 5)
        
        detectado = False
        erro_x = 0
        erro_y = 0
        identidade = "DESCONHECIDO"

        for (x, y, w, h) in faces:
            detectado = True
            
            # 1. Tenta Reconhecer
            if self.modelo_carregado:
                # O predict retorna (id, confianca)
                # Confiança: 0 = perfeito, 100+ = ruim
                id_predito, confianca = self.recognizer.predict(gray[y:y+h, x:x+w])
                
                # Se confiança for menor que 50, é muito provável que seja o dono
                if confianca < 55: 
                    identidade = "DONO"
                    cor = (0, 255, 0) # Verde
                else:
                    identidade = "DESCONHECIDO"
                    cor = (0, 0, 255) # Vermelho
            else:
                cor = (255, 0, 0) # Azul (Sem memoria)

            # 2. Desenha Feedback
            cv2.rectangle(frame, (x, y), (x+w, y+h), cor, 2)
            cv2.putText(frame, str(identidade), (x, y-5), cv2.FONT_HERSHEY_SIMPLEX, 0.8, cor, 2)

            # 3. Calcula Centro para Servos
            centro_rosto_x = x + w // 2
            centro_rosto_y = y + h // 2
            height, width, _ = frame.shape
            erro_x = centro_rosto_x - (width // 2)
            erro_y = centro_rosto_y - (height // 2)

            # Pega só o primeiro rosto e sai do loop
            break 

        cv2.imshow("Visao Argos (LBPH)", frame)
        if cv2.waitKey(1) == ord('q'): pass
            
        return detectado, erro_x, erro_y, identidade