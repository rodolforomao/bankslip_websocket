import json
import websocket
import threading

class WebSocketClientService:
    ws_url = "ws://127.0.0.1:3102"

    @staticmethod
    def get_assets_wallet():
        result_container = {}

        def on_message(ws, message):
            data = json.loads(message)
            index = 'assets_wallet'
            if "Notif" in data:
                assets_balances = data['Notif']['notif']['Balances']['balances']
                result_container['result'] = {
                    "success": True,
                    index: assets_balances,
                    "message": ""
                }
                ws.close()
            elif "Error" in data:
                result_container['result'] = {
                    "success": False,
                    index: None,
                    "message": f"Error: {data}"
                }
                ws.close()

        def on_error(ws, error):
            index = 'assets_wallet'
            result_container['result'] = {
                "success": False,
                index: None,
                "message": f"Error: {error}"
            }
            ws.close()

        def on_close(ws, close_status_code, close_msg):
            pass

        def on_open(ws):
            pass

        ws = websocket.WebSocketApp(
            WebSocketClientService.ws_url,
            on_message=on_message,
            on_error=on_error,
            on_close=on_close,
            on_open=on_open
        )

        thread = threading.Thread(target=ws.run_forever)
        thread.start()
        thread.join(timeout=10)

        return result_container.get('result', {
            "success": False,
            "assets_wallet": None,
            "message": "Timeout or no response"
        })
