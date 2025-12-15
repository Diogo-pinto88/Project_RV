from obu import OBU

class AU:
    """
    Application User (AU) - Condutor
    Representa o condutor e fornece a interface homem-máquina do sistema.
    Seu papel é limitado a solicitar autorização de estacionamento e exibir o resultado final ao condutor.
    O AU não realiza nenhuma tomada de decisão e comunica apenas com o OBU.
    """
    
    def __init__(self):
        self.obu = OBU()
    
    def request_parking(self, position=None):
        """
        Solicita autorização de estacionamento ao OBU e exibe o resultado.
        """
        result = self.obu.request_parking(position)
        self.display_result(result)
    
    def display_result(self, result):
        """
        Exibe o resultado da autorização ao condutor.
        """
        if result:
            print("Estacionamento autorizado.")
        else:
            print("Estacionamento não autorizado.")

# Exemplo de uso (para testar)
if __name__ == "__main__":
    au = AU()
    au.request_parking()  # Teste com posição padrão
    au.request_parking("zone3")  # Teste com zona proibida
