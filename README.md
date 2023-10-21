# PiSync
Easily sync media (audio, video, etc.) across multiple Raspberry Pis (or similar SBCs) for cool holiday displays or
special events!

[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=JohnBarton27_pisync&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=JohnBarton27_pisync)
[![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=JohnBarton27_pisync&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=JohnBarton27_pisync)
[![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=JohnBarton27_pisync&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=JohnBarton27_pisync)

## Running
To start the server, run:

```
python server.py
```

The PiSync server will now be running on port 5467 (this can be changed in `settings.py`).

To start any clients, run:

```
python client.py
```

## Raspberry Pi Setup
The following steps have been validated with a Raspberry Pi 4 Model B.

1. Download the latest LTS Ubuntu version for Raspberry Pi:
https://ubuntu.com/download/raspberry-pi
1. Connect the Raspberry Pi to a monitor and keyboard. Provide power, and then finish the setup process.

1. Install and enable SSH:
```
sudo apt update
sudo apt install openssh-server
sudo service ssh start
```

You can now access the Pi with:
```
ssh <username>@<pi_ip_address>
```

Once in a terminal on the Pi, you'll need to do the following:
```
# Install dependencies
sudo apt install git python3.10-venv ffmpeg net-tools vlc

# Clone this repository
git clone https://github.com/JohnBarton27/pisync.git

cd pisync

# Setup Python Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Additional Server Setup
If you want to run this via its own, ad-hoc WiFi network, designate the "server" Raspberry Pi as the "access point" Raspberry Pi and follow these instructions (on that Pi):

1. Update & upgrade the Raspberry Pi:
   ```
   sudo apt update && sudo apt upgrade -y
   ```
2. Run the following commands:
   ```
   sudo apt install hostapd dnsmasq dhcpcd5 net-tools
   sudo systemctl stop hostapd
   sudo systemctl stop dnsmasq
   ```
3. Configure a static IP for WLAN by editing the `dhcpcd` configuration:
   ```
   sudo nano /etc/dhcpcd.conf
   ```
   Add the following to the end of the file:
   ```
   interface wlan0
   static ip_address=192.168.4.1/24  # USE PREFERRED IP ADDRESS HERE
   nohook wpa_supplicant
   ```
4. Configure `dnsmasq`: First, backup the original configuration:
   ```
   sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
   ```
   THen, create a new one:
   ```
   sudo nano /etc/dnsmasq.conf
   ```
   Add the following:
   ```
   interface=wlan0
   interface wlan0
   static ip_address=192.168.1.1/24
   static routers=192.168.1.1
   static domain_name_servers=192.168.1.1
   port=0
   ```
5. Configure `hostapd`: Edit the configuration file:
   ```
   sudo nano /etc/hostapd/hostapd.conf
   ```
   Add your desired AP configurations (modify as necessary):
   ```
   interface=wlan0
   driver=nl80211
   ssid=MyPiAP
   hw_mode=g
   channel=7
   wmm_enabled=0
   macaddr_acl=0
   auth_algs=1
   ignore_broadcast_ssid=0
   wpa=2
   wpa_passphrase=MySecurePassword
   wpa_key_mgmt=WPA-PSK
   wpa_pairwise=TKIP
   rsn_pairwise=CCMP
   ```
   Tell the system where to find this config:
   ```
   sudo nano /etc/default/hostapd
   ```
   Find the line `#DAEMON_CONF=""` and replace it with:
   ```
   DAEMON_CONF="/etc/hostapd/hostapd.conf
   ```
6. Ensure nothing else is running on port 53 (default DNS port) with:
   ```
   sudo netstat -tuln | grep :53
   sudo systemctl stop systemd-resolved
   sudo systemctl disable systemd-resolved
   ```
   Backup the original `resolv.conf`:
   ```
   sudo mv /etc/resolv.conf /etc/resolv.conf.orig
   ```
   Create a new `resolv.conf` with a public DNS server (like Google's):
   ```
   echo "nameserver 127.0.0.1" | sudo tee /etc/resolv.conf
   ```
7. Start & enable services:
   ```
   sudo systemctl unmask hostapd
   sudo systemctl start hostapd
   sudo systemctl start dnsmasq
   sudo systemctl enable hostapd
   sudo systemctl enable dnsmasq
   ```

### Automatic Startup on Raspberry Pi
1. Press Super (Windows key) and search for "Startup Applications".
2. Click on the "Startup Applications" icon.
3. In the Startup Applications Preferences window, click on the "Add" button.
4. Provide a name for your command, the command itself, and a comment if desired. For example:
   - Name: PiSync Client
   - Command: `/path/to/pisync/bin/start_client.sh`
   - Comment: Start the PiSync Client
5. Click "Add" to save.