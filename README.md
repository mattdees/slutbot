An easy to install and use IRC bot designed for the #reddit-houston IRC channel

# Installation
Slut bot is written to be run on Ubuntu, I'm sure it will work just fine on other distributions, but I use ubuntu.

>    $ sudo apt-get install python-twisted-words python-twisted  python-yaml python-beautifulsoup python-enchant python-simplejson
>    
>    $ git clone https://github.com/MattDees/slutbot.git

# Configuration

Copy servers.yaml.example to servers.yaml and adjust configuration to the server/channel you want to use.

# Execution

run slutbot.py:

>    $ python slutbot.pt

# Hacking

All code must pass a standard ubuntu flake8 installation, except for E501 (line length)

>    $ python -m flake8 *.py plugins/*.py

Ideally all code should be python3 compatible, however this has not been tested yet.