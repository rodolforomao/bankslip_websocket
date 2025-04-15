from app import create_app
from app.services.ip_updater import IPUpdater

app = create_app()

if __name__ == '__main__':
    IPUpdater.send_ip_to_laravel()
    app.run(host='0.0.0.0', port=8080)
