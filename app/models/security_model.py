import os
import base64
from Crypto.Cipher import AES
import json
from dotenv import load_dotenv
load_dotenv()

class SecurityModel:
    @staticmethod
    def decrypt_payload(encoded_data):
        # Lê a chave do .env e decodifica de base64
        secret_b64 = os.getenv("WEBSOCKET_BACKEND_LOCAL_SERVER_SECRET_KEY")
        key = base64.b64decode(secret_b64)

        if len(key) != 32:
            raise ValueError(f"Chave decodificada com tamanho inválido: {len(key)} bytes")

        data = base64.b64decode(encoded_data)
        iv = data[:16]
        encrypted = data[16:]

        cipher = AES.new(key, AES.MODE_CBC, iv)
        
        # decrypted = cipher.decrypt(encrypted)
        # unpadded = SecurityModel.pkcs7_unpad(decrypted)
        #unpadded = decrypted.rstrip(b"\0")

        # return json.loads(unpadded)
        decrypted = cipher.decrypt(encrypted)
        unpadded = SecurityModel.pkcs7_unpad(decrypted)
        return json.loads(unpadded.decode("utf-8"))

    @staticmethod
    def validate_payload(payload):
        from datetime import datetime, timedelta

        token = os.getenv("WEBSOCKET_BACKEND_LOCAL_SERVER_TOKEN")
        timestamp = payload.get("timestamp")

        if payload.get("token") != token:
            return False

        if not timestamp:
            return False

        ts = datetime.fromtimestamp(timestamp)
        if abs((datetime.now() - ts).total_seconds()) > 300:
            return False

        return True

    @staticmethod
    def pkcs7_unpad(data):
        pad_len = data[-1]
        if pad_len < 1 or pad_len > 16:
            raise ValueError(f"Invalid padding length: {pad_len}")
        return data[:-pad_len]