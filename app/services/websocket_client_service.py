import json
import time
import socket
import threading
import subprocess
import websocket


class WebSocketClientService:
    ws_url = "ws://127.0.0.1:3102"
    ws_dir = "D:/enviroment/desenvolvimento/Estudos/liquid/sideswap_rust/sideswap_manager"
    MAX_ATTEMPTS = 3

    @staticmethod
    def is_websocket_online(host="127.0.0.1", port=3102, timeout=1):
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    @staticmethod
    def start_websocket_service():
        try:
            process = subprocess.Popen(
                ["cargo", "run", "--", "config/example.toml"],
                cwd=WebSocketClientService.ws_dir,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                shell=False
            )

            timeout_seconds = 5
            interval = 0.5
            waited = 0
            while waited < timeout_seconds:
                if WebSocketClientService.is_websocket_online():
                    return True
                time.sleep(interval)
                waited += interval

            print("WebSocket server not responding after starting.")
            return False

        except Exception as e:
            print("Failed to start WebSocket service:", str(e))
            return False

    @staticmethod
    def ensure_websocket_ready():
        attempt = 0
        while attempt < WebSocketClientService.MAX_ATTEMPTS:
            if WebSocketClientService.is_websocket_online():
                return True
            if WebSocketClientService.start_websocket_service():
                if WebSocketClientService.is_websocket_online():
                    return True
            attempt += 1
        return False

    @staticmethod
    def send_request(request_data, result_key, success_handler, timeout=10):
        result_container = {"result": None}
        request_sent = bool(request_data)

        def on_message(ws, message):
            try:
                data = json.loads(message)

                if "Error" in data:
                    result_container['result'] = {
                        "success": False,
                        result_key: None,
                        "message": f"Error: {data['Error']['err']['text']}"
                    }
                    ws.close()

                else:
                    result = success_handler(data)
                    if result is not None:
                        result_container['result'] = result
                        ws.close()
                    # senão ignora (ex: notificação sem relação com o pedido)

            except Exception as e:
                result_container['result'] = {
                    "success": False,
                    result_key: None,
                    "message": f"Exception parsing message: {str(e)}"
                }
                ws.close()

        def on_error(ws, error):
            result_container['result'] = {
                "success": False,
                result_key: None,
                "message": f"Error: {error}"
            }
            ws.close()

        def on_close(ws, close_status_code, close_msg):
            pass

        def on_open(ws):
            if request_sent:
                ws.send(json.dumps(request_data))

        ws = websocket.WebSocketApp(
            WebSocketClientService.ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

        thread = threading.Thread(target=ws.run_forever)
        thread.start()
        thread.join(timeout=timeout)

        return result_container.get('result') or {
            "success": False,
            result_key: None,
            "message": "Timeout or no response"
        }

    @staticmethod
    def get_assets_wallet():
        if not WebSocketClientService.ensure_websocket_ready():
            return {
                "success": False,
                "assets_wallet": None,
                "message": "WebSocket service failed to start"
            }

        def handler(data):
            if "Notif" in data and "Balances" in data["Notif"]["notif"]:
                balances = data['Notif']['notif']['Balances']['balances']
                return {
                    "success": True,
                    "assets_wallet": balances,
                    "message": ""
                }
            return None  # Ignora outras mensagens

        # Como a requisição de assets é enviada automaticamente pelo servidor,
        # não enviamos nada, só ouvimos.
        request = {}
        return WebSocketClientService.send_request(request, "assets_wallet", handler)

    @staticmethod
    def get_quote(amount, destination_address, send_asset="DePix", recv_asset="USDt"):
        if not WebSocketClientService.ensure_websocket_ready():
            return {
                "success": False,
                "recv_amount": None,
                "message": "WebSocket service failed to start"
            }

        def handler(data):
            if "Resp" in data and "GetQuote" in data["Resp"]["resp"]:
                recv_amount = data["Resp"]["resp"]["GetQuote"].get("recv_amount")
                return {
                    "success": True,
                    "recv_amount": recv_amount,
                    "message": ""
                }
            elif "Error" in data:
                return {
                    "success": False,
                    "recv_amount": None,
                    "message": f"Error: {data['Error']['err']['text']}"
                }
            return None  # Ignora mensagens irrelevantes

        request = {
            "Req": {
                "id": 1,
                "req": {
                    "GetQuote": {
                        "send_asset": send_asset,
                        "send_amount": float(amount),
                        "recv_asset": recv_asset,
                        "receive_address": destination_address
                    }
                }
            }
        }

        return WebSocketClientService.send_request(
            request, "recv_amount", handler
        )


    @staticmethod
    def get_new_liquid_address():
        if not WebSocketClientService.ensure_websocket_ready():
            return {
                "success": False,
                "new_liquid_address": None,
                "message": "WebSocket service failed to start"
            }

        def handler(data):
            if "Resp" in data and "NewAddress" in data["Resp"]["resp"]:
                address = data['Resp']['resp']['NewAddress']['address']
                return {
                    "success": True,
                    "new_liquid_address": address,
                    "message": ""
                }
            return None

        request = {"Req": {"id": 1, "req": {"NewAddress": {}}}}
        return WebSocketClientService.send_request(request, "new_liquid_address", handler)
