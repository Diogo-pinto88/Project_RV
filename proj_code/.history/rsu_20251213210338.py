import datetime
import threading

class RSU:
    """
    Road Side Unit (RSU) - Antena
    Representa a infraestrutura rodoviária e realiza tomada de decisão local.
    Está pré-configurada com informações de geofencing definindo zonas de estacionamento permitidas e proibidas.
    Ao receber uma solicitação de estacionamento do OBU, verifica a posição do veículo, responde com o resultado da autorização,
    e, se a zona for proibida, inicia um temporizador para ações de fiscalização.
    """
    
    def __init__(self):
        # Zonas permitidas (exemplo simples com strings; em produção, usar coordenadas GPS)
        self.allowed_zones = ["zone1", "zone2"]
    
    def check_parking(self, position, timestamp):
        """
        Verifica se o estacionamento é permitido na posição dada.
        Retorna True se autorizado, False caso contrário.
        Se proibido, inicia temporizador para ação de fiscalização.
        """
        allowed = position in self.allowed_zones
        if not allowed:
            # Inicia temporizador para ação de fiscalização (exemplo: 10 segundos)
            timer = threading.Timer(10, lambda: print(f"Ação de fiscalização iniciada para posição: {position}"))
            timer.start()
        return allowed
