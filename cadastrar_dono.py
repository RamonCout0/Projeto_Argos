import cv2
import os
import numpy as np

print("--- CADASTRO DE DONO (SISTEMA LBPH) ---")
print("Olhe para a câmera. O sistema vai tirar 30 fotos rápidas.")
print("Pressione 's' para começar.")

# Cria pasta para salvar as fotos temporárias
if not os.path.exists("dados_face"):
    os.makedirs("dados_face")

# Carrega o detector de rostos padrão do OpenCV
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
cap = cv2.VideoCapture(0)

contagem = 0
treinando = False

while True:
    ret, frame = cap.read()
    if not ret: break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        if treinando:
            contagem += 1
            # Salva o rosto recortado em cinza
            rosto_recortado = gray[y:y+h, x:x+w]
            cv2.imwrite(f"dados_face/dono.{contagem}.jpg", rosto_recortado)
            print(f"Foto {contagem}/30 capturada...")

    cv2.putText(frame, f"Fotos: {contagem}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.imshow('Cadastro Argos', frame)

    k = cv2.waitKey(1) & 0xFF
    if k == ord('s') and not treinando:
        treinando = True
    elif k == ord('q') or contagem >= 30:
        break

cap.release()
cv2.destroyAllWindows()

# --- FASE DE TREINAMENTO ---
if contagem >= 30:
    print("\n[PROCESSANDO] Treinando o cérebro visual...")
    
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    detector = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    image_paths = [os.path.join("dados_face", f) for f in os.listdir("dados_face")]
    face_samples = []
    ids = []

    for image_path in image_paths:
        img_numpy = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        # O ID do dono será sempre 1
        ids.append(1)
        face_samples.append(img_numpy)

    recognizer.train(face_samples, np.array(ids))
    
    # Salva o modelo treinado
    recognizer.write('treinador_argos.yml')
    print("\n✅ SUCESSO! Arquivo 'treinador_argos.yml' criado.")
    print("Agora pode rodar o main.py")
else:
    print("\n[CANCELADO] Não tirou fotos suficientes.")