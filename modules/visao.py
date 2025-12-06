import cv2
import mediapipe as mp
import time

class OlhosArgos:
    def __init__(self):
        print("👁️ Inicializando Rastreamento Facial...")
        
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_draw = mp.solutions.drawing_utils
        
        # model_selection=0 é para rostos pertos (até 2 metros)
        # model_selection=1 é para rostos longes (até 5 metros)
        self.face_detection = self.mp_face_detection.FaceDetection(
            model_selection=0, min_detection_confidence=0.6
        )
        
        self.cap = cv2.VideoCapture(0)
        self.largura_cam = 640
        self.altura_cam = 480
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.largura_cam)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.altura_cam)

        # O Centro exato da imagem
        self.centro_x_tela = self.largura_cam // 2
        self.centro_y_tela = self.altura_cam // 2

    def ver(self):
        """
        Retorna: (detectou_algo, erro_x, erro_y)
        erro_x > 0: Rosto está à direita
        erro_x < 0: Rosto está à esquerda
        """
        sucesso, img = self.cap.read()
        if not sucesso: return False, 0, 0

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        resultados = self.face_detection.process(img_rgb)
        
        detectado = False
        erro_x = 0
        erro_y = 0

        if resultados.detections:
            detectado = True
            # Pega o primeiro rosto (o mais confiável)
            rosto = resultados.detections[0]
            
            # Desenha a caixa ao redor do rosto
            self.mp_draw.draw_detection(img, rosto)
            
            # --- CÁLCULO DO CENTRO DO ROSTO ---
            bboxC = rosto.location_data.relative_bounding_box
            
            # Converte coordenadas relativas (0.0 a 1.0) para pixels
            x = int(bboxC.xmin * self.largura_cam)
            y = int(bboxC.ymin * self.altura_cam)
            w = int(bboxC.width * self.largura_cam)
            h = int(bboxC.height * self.altura_cam)
            
            # O nariz/centro do rosto
            centro_rosto_x = x + (w // 2)
            centro_rosto_y = y + (h // 2)
            
            # Desenha o alvo no nariz
            cv2.circle(img, (centro_rosto_x, centro_rosto_y), 5, (0, 255, 0), -1)
            # Desenha linha do centro da tela até o nariz (Visualizar o erro)
            cv2.line(img, (self.centro_x_tela, self.centro_y_tela), 
                     (centro_rosto_x, centro_rosto_y), (0, 255, 255), 2)

            # --- CÁLCULO DO ERRO (Matemática para os servos) ---
            # Se for negativo, está na esquerda. Se positivo, direita.
            erro_x = centro_rosto_x - self.centro_x_tela
            erro_y = centro_rosto_y - self.centro_y_tela

        # Desenha uma mira no centro da tela para referência
        cv2.circle(img, (self.centro_x_tela, self.centro_y_tela), 2, (0, 0, 255), -1)
        
        cv2.imshow("Visão do Argos (Rastreio)", img)
        cv2.waitKey(1)
        
        return detectado, erro_x, erro_y

    def desligar(self):
        self.cap.release()
        cv2.destroyAllWindows()