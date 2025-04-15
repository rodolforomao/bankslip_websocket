import requests
from config import LARAVEL_NOTIFY_URL, LARAVEL_TOKEN

class IPUpdater:
    @staticmethod
    def get_public_ip() -> str:
        return requests.get('https://api.ipify.org').text

    @staticmethod
    def send_ip_to_laravel():
        ip = IPUpdater.get_public_ip()
        try:
            res = requests.post(LARAVEL_NOTIFY_URL, json={
                'token': LARAVEL_TOKEN,
                'ip': ip
            })
            print(f"[IP Atualizado] IP: {ip} | Resposta: {res.text}")
        except Exception as e:
            print(f"[Erro ao atualizar IP] {e}")
