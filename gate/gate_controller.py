import requests


class GateController:

    def __init__(self, esp_ip):
        self.esp_ip = esp_ip
 

    def open_gate(self, plate):

        try:
            response = requests.post(
                f"http://{self.esp_ip}/open_gate",
                timeout=2
            )

            if response.status_code == 200:
                print("BRAMA OTWARTA dla:", plate)
                return True
            else:
                print("ESP odpowiedzialo bledem:", response.status_code)
                return False

        except requests.exceptions.RequestException as e:
            print("BLAD POLACZENIA Z ESP:", e)
            return False