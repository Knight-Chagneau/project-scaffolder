# ⬡ Project Scaffolder

Outil portable de création automatique de structures de projets clients.  
Fonctionne **sans installation** et **sans droit administrateur**, sous Windows et Linux.

---

## Fonctionnalités

- 📁 Génère en un clic l'arborescence complète d'un nouveau projet
- ✅ Cases à cocher pour choisir exactement ce qu'on veut créer
- ⚙️ Panneau de configuration pour gérer ses propres templates (dossiers + fichiers avec contenu pré-rempli)
- 💾 Configuration sauvegardée en JSON, modifiable manuellement
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

---

## Structure du projet

```
├── app.py          # Application principale
├── build.py        # Script de build PyInstaller
├── config.json     # Templates par défaut      
└── requirements.txt
```

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
