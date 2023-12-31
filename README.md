# python-web-remote-control
A web-based remote control via WoL and SSH in python.

## Installation

At first you have to install following:

```
pip install wakeonlan
pip install http.server

sudo apt update
sudo apt install sshpass -y
```

Then you have to download the script and make it executable:

```
cd /opt
wget https://raw.githubusercontent.com/Michdo93/python-web-remote-control/main/handler.py
chmod +x handler.py
```

Then you have to create a service with `sudo nano /etc/systemd/system/web_remote_handler.service`:

```
[Unit]
Description=Web Remote Handler
After=network-online.target

[Service]
Type=simple
User=<user>
Group=<user>
UMask=002
WorkingDirectory=/opt
ExecStart=/usr/bin/python3 /opt/handler.py
Restart=on-failure
RestartSec=30s
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=web-remote-handler

[Install]
WantedBy=multi-user.target
```

You can then start and enable the service with:

```
sudo systemctl start web-remote-handler
sudo systemctl enable web-remote-handler
```

## Customization

You can change the following lines:

```
    instances = [
        WoLHandler('192.168.1.100', '00:11:22:33:44:55', 'user1', 'password1'),
        WoLHandler('192.168.1.101', '00:11:22:33:44:56', 'user2', 'password2'),
        # Add more instances as needed
    ]
```
