# Générateur Kiosque - Instructions

Résumé rapide
- Interface graphique légère pour charger et exécuter le script `kiosque_trefle_4petales_dome22.py`.

Prérequis
- Python 3.x (pour les tests et pre-commit)
- FreeCAD (si vous voulez exécuter l'interface et générer la géométrie)

Installation des outils de développement
```powershell
python -m pip install --user pre-commit pytest
python -m pip install -r requirements.txt  # installe pytest si besoin
```

Activer les hooks `pre-commit`
```powershell
python -m pre_commit install
pre-commit run --all-files
```

Exécuter les tests locaux
```powershell
python -m pytest -q
```

Utilisation de l'interface (FreeCAD)
- Ouvrez FreeCAD, puis exécutez `interface_ultrasimple.py` depuis l'éditeur ou `python` intégré à FreeCAD.
- Modifiez la variable `chemin_script` dans `interface_ultrasimple.py` ou utilisez le bouton `📂 Choisir un script .py`.

Notes
- Les hooks préconfigurés exécutent `black`, `isort`, `flake8` et un test smoke `pytest` avant commit.
- Le workflow CI lance `pytest` sur GitHub Actions lors des push/PR.

Contact
- Si vous voulez que j'ajoute un README plus détaillé (exemples, capture d'écran, ou étapes FreeCAD), dites-le.
[![Repo](https://img.shields.io/badge/repo-trefle_kiosque-blue)](https://github.com/biozergy/trefle_kiosque)

README â€” GÃ©nÃ©rateur Kiosque TrÃ¨fle (Interface Ultra Simple)

RÃ©sumÃ©
------
Ce dÃ©pÃ´t contient une interface graphique simple (`interface_ultrasimple.py`) qui charge de faÃ§on sÃ»re
le script principal `kiosque_trefle_4petales_dome22.py` et permet de gÃ©nÃ©rer le kiosque avec
paramÃ¨tres clÃ©s (rayon pÃ©tales, espacement, hauteur montants, hauteur dÃ´me, matÃ©riau, vent, FS).

Fichiers modifiÃ©s/ajoutÃ©s
-------------------------
- `interface_ultrasimple.py`  (modifiÃ©) â€” charge sÃ©curisÃ© via `importlib`, introspection, UI Ã©tendue
- `kiosque_trefle_4petales_dome22.py` (inchangÃ©) â€” script principal contenant la classe `KiosqueTrefleFonctionnel`
- `README.md` (ajoutÃ©)

Lancement (console Python de FreeCAD)
-------------------------------------
1) Depuis FreeCAD (Python console) :

```python
import sys
sys.path.append(r"C:\Users\martin-cochera\Documents\TREFLE_PROJECT\SCRIPTS_PARAMETRIQUES")
import interface_ultrasimple
iface = interface_ultrasimple.InterfaceUltraSimple(r"C:\Users\martin-cochera\Documents\TREFLE_PROJECT\SCRIPTS_PARAMETRIQUES\kiosque_trefle_4petales_dome22.py")
iface.exec_()
```

2) Ou laisser l'interface demander le script :

```python
import interface_ultrasimple
interface_ultrasimple.trouver_script_manuellement()
```

Test rapide
-----------
- Ouvrir l'interface, rÃ©gler : `Rayon pÃ©tales`, `Espacement`, `Hauteur montants`, `Hauteur DÃ´me (mm)`, `MatÃ©riau`, `Vitesse vent`, `Facteur de sÃ©curitÃ©`.
- Cliquer `ðŸ”§ GÃ©nÃ©rer avec paramÃ¨tres` pour gÃ©nÃ©rer via `KiosqueTrefleFonctionnel` si disponible.
- Utiliser `ðŸ’¡ Conseil dimensionnement` pour une recommandation heuristique.
- VÃ©rifiez la console FreeCAD pour messages d'erreur/confirmation.

Commit Git (exÃ©cuter dans PowerShell Ã  la racine du projet)
---------------------------------------------------------
```powershell
cd "C:\Users\martin-cochera\Documents\TREFLE_PROJECT\SCRIPTS_PARAMETRIQUES"
git init                      # si pas encore de repo
git add interface_ultrasimple.py README.md
git commit -m "Add safe loader, UI introspection, dome height control and README"
```

Notes & prochaines amÃ©liorations possibles
-----------------------------------------
- GÃ©nÃ©rer automatiquement des champs UI pour les paramÃ¨tres de fonctions via `inspect.signature`.
- ExÃ©cuter la gÃ©nÃ©ration dans un subprocess pour isoler FreeCAD des erreurs de script.
- Ajouter sauvegarde des paramÃ¨tres (profil), export PDF des recommandations, et tests unitaires.

Si vous voulez, je peux :
- crÃ©er le commit pour vous (si vous m'autorisez Ã  exÃ©cuter des commandes git ici),
- ajouter un petit script de tests.

Fin du README
