import wave
import math
import struct

def criar_bip(nome_arquivo, frequencia, duracao):
    print(f"Gerando {nome_arquivo}...")
    sample_rate = 44100
    n_samples = int(sample_rate * duracao)
    
    with wave.open(nome_arquivo, 'w') as obj:
        obj.setnchannels(1) # Mono
        obj.setsampwidth(2) # 2 bytes
        obj.setframerate(sample_rate)
        
        for i in range(n_samples):
            # Gera a onda senoidal
            value = int(32767.0 * math.sin(2.0 * math.pi * frequencia * i / sample_rate))
            data = struct.pack('<h', value)
            obj.writeframesraw(data)

# Gera o som de "Ouvir" (Agudo e curto - 1200Hz)
criar_bip("bip_ouvir.wav", 1200, 0.15)

# Gera o som de "Erro" (Grave e longo - 200Hz)
criar_bip("bip_erro.wav", 200, 0.4)

print("✅ Sons gerados com sucesso!")