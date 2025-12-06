import time

class HexapodDriver:
    def __init__(self, simulacao=True):
        self.simulacao = simulacao
        
        # --- ESTADO DO PESCOÇO/CORPO ---
        # 90 graus é o centro (olhando pra frente)
        self.pan_atual = 90.0  # Horizontal (Esquerda/Direita)
        self.tilt_atual = 90.0 # Vertical (Cima/Baixo)
        
        # Limites físicos dos servos (para não quebrar o pescoço)
        self.limite_min = 0
        self.limite_max = 180

        if self.simulacao:
            print("🔧 [MOCK]: Sistema de servos virtuais iniciado (Centro=90°).")
        else:
            # from adafruit_servokit import ServoKit
            # self.kit = ServoKit(channels=16)
            pass

    def atualizar_rastreio(self, erro_x, erro_y):
        """
        Recebe o erro em pixels e move os servos suavemente para centralizar.
        """
        # Sensibilidade: Quanto maior, mais rápido ele gira. 
        # Para hexápode pesado, use valor baixo (0.1 a 0.5)
        ganho = 0.15 
        
        # --- CÁLCULO HORIZONTAL (PAN) ---
        # Se o erro_x é positivo (rosto na direita), subtraímos do ângulo para girar direita 
        # (Nota: A direção depende da montagem do servo, se ficar invertido, troque - por +)
        movimento_x = erro_x * ganho
        
        # Como o erro é em pixels (ex: 200), precisamos reduzir a escala
        # Vamos mover apenas 1 ou 2 graus por frame para ser suave
        if movimento_x > 1.0: movimento_x = 2.0
        elif movimento_x < -1.0: movimento_x = -2.0
        else: movimento_x = 0
        
        self.pan_atual -= movimento_x
        
        # --- CÁLCULO VERTICAL (TILT) ---
        movimento_y = erro_y * ganho
        if movimento_y > 1.0: movimento_y = 2.0
        elif movimento_y < -1.0: movimento_y = -2.0
        else: movimento_y = 0
        
        self.tilt_atual -= movimento_y

        # TRAVA DE SEGURANÇA (Clamp)
        # Garante que não mandamos o servo para 200 graus (o que quebraria ele)
        self.pan_atual = max(self.limite_min, min(self.pan_atual, self.limite_max))
        self.tilt_atual = max(self.limite_min, min(self.tilt_atual, self.limite_max))

        if self.simulacao:
            self._desenhar_cabeca_terminal()
        else:
            # self.kit.servo[0].angle = self.pan_atual
            # self.kit.servo[1].angle = self.tilt_atual
            pass

    def _desenhar_cabeca_terminal(self):
        """Visualização ASCII da posição da cabeça"""
        # Cria uma barra visual: [      |      ]
        barra_tamanho = 20
        posicao_relativa = int((self.pan_atual / 180) * barra_tamanho)
        
        barra = ["-"] * barra_tamanho
        if 0 <= posicao_relativa < barra_tamanho:
            barra[posicao_relativa] = "O" # Onde a cabeça está
        
        barra_str = "".join(barra)
        print(f"\r🕷️ SERVOS: [{barra_str}] Pan:{self.pan_atual:.1f}° Tilt:{self.tilt_atual:.1f}°", end="")

    def executar_acao(self, comando):
        # Mantivemos as funções antigas caso precise
        if comando == "PARAR": print("\n>>> PARANDO MOTORES")
        elif comando == "SAUDACAO": print("\n>>> TCHAUZINHO")