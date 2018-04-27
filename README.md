clockwork-bot
=============

Discord bot for [Clockwork](https://forum.clockworkpi.com/t/a-discord-for-the-community/264/2) channel.

Dependencies
------------

* Python 3.5+

Setup
-----

1. Download source and `cd` to it's root directory.

2. Setup virtual environment
```bash
$ python3 -m venv env
```

3. Source the virtual environment
```bash
$ source env/bin/activate
```

4. Install required packages
```bash
$ pip3 install -r requirements.txt
```

5. Create the config file and populate the settings
```bash
$ cp config.example.json config.json
```

6. Set the permissions for the script
```bash
$ chmod +x bot.py
```

7. Start the bot
```bash
$ ./bot.py
```

Features:
---------

* Broadcast updates from Clockwork team on Discourse community forum (from the [GameShell Updates](https://forum.clockworkpi.com/t/gameshell-updates/257) thread)
