import datetime
from rsu import RSU

class OBU:
    """
    On-Board Unit (OBU) - Veículo
    Trata da lógica do veículo e comunicação.
    Recebe a solicitação de estacionamento do AU, determina a posição do veículo, gera um timestamp,
    e envia essas informações para o RSU.
    Após receber a decisão do RSU, o OBU encaminha o resultado final para o AU.
    O OBU não decide se o estacionamento é permitido.
    """
    
    def __init__(self):
        self.rsu = RSU()
    
    def request_parking(self, position=None):
        """
        Recebe solicitação do AU, determina posição, gera timestamp, envia para RSU e retorna resultado.
        """
        if position is None:
            # Simulação: determinar posição (em produção, usar GPS)
            position = "zone1"  # Exemplo; pode ser alterado para simular diferentes zonas
        
        timestamp = datetime.datetime.now()
        
        # Envia para RSU
        result = self.rsu.check_parking(position, timestamp)
        
        # Retorna resultado para AU
        return result
