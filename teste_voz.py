import pyttsx3

print("--- INICIANDO TESTE DE VOZ ---")

try:
    # Tenta forçar o driver do Windows (SAPI5)
    engine = pyttsx3.init(driverName='sapi5') 
    
    # Lista as vozes que ele encontrou no seu PC
    voices = engine.getProperty('voices')
    print(f"Vozes encontradas: {len(voices)}")
    
    for voice in voices:
        print(f" - ID: {voice.id}")
        print(f" - Nome: {voice.name}")

    # Configurações básicas
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)

    print("Tentando falar agora...")
    engine.say("Teste de áudio do sistema Argos. Um, dois, três.")
    engine.runAndWait()
    
    print("--- FIM DO TESTE ---")

except Exception as e:
    print(f"\n[ERRO CRÍTICO]: {e}")