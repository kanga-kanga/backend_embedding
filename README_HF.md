# Déploiement avec l'API Hugging Face Inference

Cette petite app Flask appelle l'API Inference de Hugging Face pour obtenir des embeddings.

Variables d'environnement requises
- `HF_TOKEN` : ton token Hugging Face (scope `read`).
- `HF_MODEL` (optionnel) : identifiant du modèle Hugging Face (par défaut `paraphrase-multilingual-MiniLM-L12-v2`).

Installer les dépendances
```bash
python -m venv venv
venv/Scripts/activate    # Windows
# ou: source venv/bin/activate
pip install -r requirements.txt
```

Lancer localement
```bash
set HF_TOKEN=hf_xxx...   # Windows PowerShell (ou setx pour persistant)
export HF_TOKEN=hf_xxx... # macOS/Linux
python app.py
```

Tester
```bash
curl -X POST -H "Content-Type: application/json" -d '{"text":"Bonjour, comment ça va ?"}' http://127.0.0.1:8000/embed
```

Déploiement sur PythonAnywhere
- Créer un virtualenv avec la même version de Python que le web app.
- Installer `requirements.txt`.
- Uploader `app.py` et ce README.
- Configurer le WSGI pour exposer l'app Flask (voir dashboard PythonAnywhere) et ajouter la variable d'environnement `HF_TOKEN` dans le Dashboard -> Web -> Environment variables.

Limitations
- Usage soumis aux quotas et latences de l'API Hugging Face Inference.
- Pour production à fort volume, envisager une solution auto-hébergée ou un plan payant HF.
