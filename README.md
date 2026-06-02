# ⬡ Project Scaffolder

Outil portable de création automatique de structures de projets clients.  
Fonctionne **sans installation** et **sans droits administrateur**, sous Windows et Linux.

---

## Fonctionnalités

- 📁 Génère en un clic l'arborescence complète d'un nouveau projet
- ✅ Cases à cocher pour choisir exactement ce qu'on veut créer
- ⚙️ Panneau de configuration pour gérer ses propres templates (dossiers + fichiers avec contenu pré-rempli)
- 💾 Configuration sauvegardée en JSON, modifiable à la main
- 🖼️ Support du logo PNG personnalisé
- 🪟 Exécutable portable : un seul fichier `.exe` (Windows) ou binaire (Linux)

---

## Utilisation

### Lancer depuis les sources

```bash
# 1. Créer et activer le venv
python3 -m venv .venv
source .venv/bin/activate        # Linux / macOS
.venv\Scripts\activate           # Windows

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer
python app.py
```

### Générer un exécutable portable

```bash
python build.py
```

L'exécutable est généré dans `dist/`.  
Distribue uniquement **2 fichiers** :
- `ProjectScaffolder` (ou `.exe` sur Windows)
- `config.json`

Et optionnellement `logo.png` pour afficher ton logo.

---

## Structure du projet

```
├── app.py          # Application principale
├── build.py        # Script de build PyInstaller
├── config.json     # Templates par défaut
├── logo.png        # Ton logo (optionnel)
└── requirements.txt
```

---

## Personnalisation

### Ton nom et les infos de l'app

Dans `app.py`, modifie les constantes en bas du fichier :

```python
APP_NAME        = "Project Scaffolder"
APP_VERSION     = "1.0.0"
APP_AUTHOR      = ""        # ← ton nom ici
APP_DESCRIPTION = "..."
APP_LICENSE     = "MIT License — Logiciel libre et open source"
APP_YEAR        = "2025"
```

### Logo personnalisé

Place un fichier `logo.png` à côté de l'exécutable.  
Format recommandé : PNG avec transparence, carré, minimum 128×128 px.  
Sans logo, un logo vectoriel de secours s'affiche automatiquement.

---

## Build automatique (GitHub Actions)

À chaque push sur `main`, les workflows CI génèrent automatiquement :
- `ProjectScaffolder` (Linux)
- `ProjectScaffolder.exe` (Windows)

Les exécutables sont disponibles dans l'onglet **Actions → Artifacts** du repo.

---

## Licence

MIT License — Logiciel libre et open source.  
Voir [LICENSE](LICENSE).
