# PiSync
Easily sync media (audio, video, etc.) across multiple Raspberry Pis (or similar SBCs) for cool holiday displays or
special events!

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
sudo apt install git python3.10-venv ffmpeg net-tools

# Clone this repository
git clone https://github.com/JohnBarton27/pisync.git

cd pisync

# Setup Python Environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```