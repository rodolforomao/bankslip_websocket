
from flask import Blueprint, request, jsonify
from app.models.security_model import SecurityModel
from app.services.websocket_client_service import WebSocketClientService

request_bp = Blueprint('request_bp', __name__)

@request_bp.route('/execute', methods=['POST'])
def execute():
    try:
        encrypted_data = request.json.get('data')
        payload = SecurityModel.decrypt_payload(encrypted_data)

        if not SecurityModel.validate_payload(payload):
            return jsonify({'error': 'Token ou timestamp inválido'}), 403

        funcao = payload.get('func')

        if funcao == 'minha_funcao':
            return jsonify({'resultado': 'Função teste executada com sucesso!'})
        elif funcao == 'get_assets_wallet':
            result = WebSocketClientService.get_assets_wallet()
            return jsonify(result)

        return jsonify({'error': 'Função desconhecida'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500
