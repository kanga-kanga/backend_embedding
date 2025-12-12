"""Simple WSGI launcher for PythonAnywhere.

Remplacez 'yourusername' par votre nom d'utilisateur PythonAnywhere
et ajustez les chemins du project_home et du virtualenv si nécessaire.
"""
import sys
import os

project_home = '/home/HeritierKM/backend_embedding/'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Virtualenv activation (adapt path si nécessaire)
activate_this = '/home/HeritierKM/venvs/embeds-env/bin/activate_this.py'
if os.path.exists(activate_this):
    with open(activate_this) as f:
        exec(f.read(), dict(__file__=activate_this))

from app import app as application
