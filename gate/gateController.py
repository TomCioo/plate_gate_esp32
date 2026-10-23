import requests
import time
import config

class GateController:

    def __init__(self, esp_ip):
        self.esp_ip = config.ESP_IP
        self.lastOpenTime = 0

    def openGate(self, plate):

        try:
            response = requests.post(
                f"http://{self.esp_ip}/open_gate",
                timeout=2
            )

            if response.status_code == 200:
                print("BRAMA OTWARTA dla:", plate)
                self.lastOpenTime = time.time()
            else:
                print("ESP odpowiedzialo bledem:", response.status_code)

        except requests.exceptions.RequestException as e:
            print("BLAD POLACZENIA Z ESP:", e)