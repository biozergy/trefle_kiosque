README — Générateur Kiosque Trèfle (Interface Ultra Simple)

Résumé
------
Ce dépôt contient une interface graphique simple (`interface_ultrasimple.py`) qui charge de façon sûre
le script principal `kiosque_trefle_4petales_dome22.py` et permet de générer le kiosque avec
paramètres clés (rayon pétales, espacement, hauteur montants, hauteur dôme, matériau, vent, FS).

Fichiers modifiés/ajoutés
-------------------------
- `interface_ultrasimple.py`  (modifié) — charge sécurisé via `importlib`, introspection, UI étendue
- `kiosque_trefle_4petales_dome22.py` (inchangé) — script principal contenant la classe `KiosqueTrefleFonctionnel`
- `README.md` (ajouté)

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
- Ouvrir l'interface, régler : `Rayon pétales`, `Espacement`, `Hauteur montants`, `Hauteur Dôme (mm)`, `Matériau`, `Vitesse vent`, `Facteur de sécurité`.
- Cliquer `🔧 Générer avec paramètres` pour générer via `KiosqueTrefleFonctionnel` si disponible.
- Utiliser `💡 Conseil dimensionnement` pour une recommandation heuristique.
- Vérifiez la console FreeCAD pour messages d'erreur/confirmation.

Commit Git (exécuter dans PowerShell à la racine du projet)
---------------------------------------------------------
```powershell
cd "C:\Users\martin-cochera\Documents\TREFLE_PROJECT\SCRIPTS_PARAMETRIQUES"
git init                      # si pas encore de repo
git add interface_ultrasimple.py README.md
git commit -m "Add safe loader, UI introspection, dome height control and README"
```

Notes & prochaines améliorations possibles
-----------------------------------------
- Générer automatiquement des champs UI pour les paramètres de fonctions via `inspect.signature`.
- Exécuter la génération dans un subprocess pour isoler FreeCAD des erreurs de script.
- Ajouter sauvegarde des paramètres (profil), export PDF des recommandations, et tests unitaires.

Si vous voulez, je peux :
- créer le commit pour vous (si vous m'autorisez à exécuter des commandes git ici),
- ajouter un petit script de tests.

Fin du README
