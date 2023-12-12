from http.server import BaseHTTPRequestHandler, HTTPServer
from wakeonlan import send_magic_packet
import json
import subprocess
import threading
import shlex

class WoLHandler(BaseHTTPRequestHandler):
    def __init__(self, target_ip, target_mac, target_username, target_password, *args, **kwargs):
        self.target_ip = target_ip
        self.target_mac = target_mac
        self.target_username = target_username
        self.target_password = target_password
        super().__init__(*args, **kwargs)

    def do_GET(self):
        if self.path == '/':
            online_status = self.is_online()
            button_text = 'Ausschalten' if online_status else 'Einschalten'

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>WoL und Ausschalten</title>
            </head>
            <body>
                <h1>Computersteuerung</h1>
                <button id="controlButton">{button_text}</button>
            
                <script>
                    var button = document.getElementById('controlButton');
                    button.addEventListener('click', function() {{
                        var action = button.innerText.toLowerCase();
                        if (action === 'einschalten') {{
                            sendWoLPacket();
                        }} else if (action === 'ausschalten') {{
                            shutdownComputer();
                        }}
                    }});
                    
                    function sendWoLPacket() {{
                        fetch('/wol', {{
                            method: 'POST',
                            headers: {{
                                'Content-Type': 'application/json'
                            }},
                            body: JSON.stringify({{ mac: '{self.target_mac}' }})
                        }})
                        .then(response => response.text())
                        .then(responseText => {{
                            alert(responseText);
                        }});
                    }}
                    
                    function shutdownComputer() {{
                        fetch('/shutdown', {{
                            method: 'POST'
                        }})
                        .then(response => response.text())
                        .then(responseText => {{
                            alert(responseText);
                        }});
                    }}
                </script>
            </body>
            </html>
            """
            self.wfile.write(html_content.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == '/wol':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            post_data = json.loads(post_data)

            mac_address = post_data.get('mac', None)
            if mac_address:
                send_magic_packet(mac_address)
                response_text = 'WoL-Paket erfolgreich gesendet an ' + mac_address
            else:
                response_text = 'Ungültige MAC-Adresse'

            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(response_text.encode())
        elif self.path == '/shutdown':
            response_text = self.shutdown_computer()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(response_text.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def is_online(self):
        try:
            response = subprocess.check_output(['ping', '-c', '1', self.target_ip])
            return '1 packets transmitted, 1 received' in response.decode()
        except subprocess.CalledProcessError:
            return False

    def shutdown_computer(self):
        try:
            # Construct the sshpass command to use the target_username and target_password
            sshpass_command = f'sshpass -p {shlex.quote(self.target_password)}'
            
            # Construct the full ssh command with sshpass
            ssh_command = [
                sshpass_command,
                'ssh',
                f'{self.target_username}@{self.target_ip}',
                'sudo',
                'shutdown',
                '-h',
                'now'
            ]

            subprocess.run(ssh_command, check=True)
            return 'Ausschaltbefehl gesendet.'
        except subprocess.CalledProcessError:
            return 'Fehler beim Senden des Ausschaltbefehls.'

def run_server():
    # Use a list of instances with different parameters
    instances = [
        WoLHandler('192.168.1.100', '00:11:22:33:44:55', 'user1', 'password1'),
        WoLHandler('192.168.1.101', '00:11:22:33:44:56', 'user2', 'password2'),
        # Add more instances as needed
    ]

    # Run servers for each instance
    for instance in instances:
        server_address = ('', 8080)
        httpd = HTTPServer(server_address, instance)
        print(f'Server läuft auf Port 8080 für {instance.target_ip}...')
        threading.Thread(target=httpd.serve_forever).start()

if __name__ == '__main__':
    run_server()
