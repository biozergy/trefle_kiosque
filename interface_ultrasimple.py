"""
🏗️ INTERFACE ULTRA SIMPLE POUR KIOSQUE TRÈFLE
Version qui CHARGERA votre script à coup sûr
"""

import os
import sys

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

# Ajouter le répertoire courant au path pour importer config et retrofits
_script_dir = os.path.dirname(os.path.abspath(__file__))
if _script_dir not in sys.path:
    sys.path.insert(0, _script_dir)

# Importer config et retrofits pour les presets et options modulaires
try:
    from config import (
        PRESETS,
        RETROFIT_OPTIONS,
        calculate_secondary_params,
        estimate_costs,
    )

    CONFIG_AVAILABLE = True
    print("✅ config.py chargé")
except ImportError as e:
    CONFIG_AVAILABLE = False
    print(f"⚠️  config.py non disponible - fonctionnalités présets désactivées ({e})")

try:
    from retrofits import RetrofitManager  # noqa: F401

    RETROFITS_AVAILABLE = True
    print("✅ retrofits.py chargé")
except ImportError as e:
    RETROFITS_AVAILABLE = False
    print(f"⚠️  retrofits.py non disponible - options modulaires désactivées ({e})")

print("\n" + "=" * 60)
print("🏗️ INTERFACE ULTRA SIMPLE - CHARGEMENT GARANTI")
print("=" * 60)


class InterfaceUltraSimple(QtGui.QDialog):
    def __init__(self, chemin_script=None):
        super(InterfaceUltraSimple, self).__init__()

        # Initialiser le gestionnaire de retrofits (si disponible)
        self.retrofit_manager = None
        self.selected_retrofits = {}  # {nom_retrofit: bool}
        self.secondary_params = {}  # Paramètres calculés (anneau, montants, etc.)
        self.cost_estimate = {}  # Estimation coût
        self.functions_map = {}  # {nom_fonction: callable}
        self.classes_map = {}  # {nom_classe: class}

        # CHEMIN EXPLICITE - MODIFIEZ ICI !!!
        if chemin_script is None:
            # Essayer de détecter automatiquement dans le répertoire courant
            auto_path = os.path.join(os.getcwd(), "kiosque_trefle_4petales_dome22.py")
            if os.path.exists(auto_path):
                self.chemin_script = auto_path
            else:
                # Fallback: chemin par défaut (à modifier)
                self.chemin_script = r"C:\path\to\kiosque_trefle_4petales_dome22.py"
        else:
            self.chemin_script = chemin_script

        print(f"🔍 Chemin du script: {self.chemin_script}")

        # Charger IMMÉDIATEMENT le script
        self.fonctions_chargees = self.charger_script_explicitement()

        # Interface simple
        self.setup_ui()

    def charger_script_explicitement(self):
        """Charge le script de manière EXPLICITE"""
        try:
            # Vérifier si le fichier existe
            if not os.path.exists(self.chemin_script):
                print(f"❌ Fichier non trouvé: {self.chemin_script}")

                # Demander à l'utilisateur
                fichier, _ = QtGui.QFileDialog.getOpenFileName(
                    None,
                    "Où est votre script kiosque_trefle_4petales_dome22.py ?",
                    os.path.expanduser("~"),
                    "Python Files (*.py)",
                )

                if fichier:
                    self.chemin_script = fichier
                else:
                    return []

            print(f"✅ Fichier trouvé: {self.chemin_script}")

            # ANALYSER le script pour trouver les fonctions
            import importlib.util
            import inspect

            # Charger le module de façon isolée (importlib)
            print("⚡ Chargement sûr du module...")
            try:
                spec = importlib.util.spec_from_file_location(
                    "kiosque_module", self.chemin_script
                )
                module = importlib.util.module_from_spec(spec)
                # Exécuter le module dans son propre espace de noms
                spec.loader.exec_module(module)
                self.module_loaded = module
                print(f"✅ Module chargé: {getattr(module, '__name__', '<module>')}")
            except Exception as e:
                print(f"❌ Erreur import module: {e}")
                import traceback

                traceback.print_exc()
                return []

            # Chercher CLASSES ET FONCTIONS (pas juste fonctions)
            # Exclure les helpers attachés à InterfaceUltraSimple
            excluded = {
                "generer_avec_parametres",
                "montrer_conseil",
                "choisir_script",
                "_append_log",
            }

            # 1. Chercher les CLASSES avec "Kiosque" dans le nom
            classes_trouvees = [
                name
                for name, obj in inspect.getmembers(module, inspect.isclass)
                if getattr(obj, "__module__", "") == module.__name__
                and "kiosque" in name.lower()
            ]
            print(f"🔍 Classes trouvées: {len(classes_trouvees)}")
            for name in classes_trouvees:
                print(f"   • {name}")

            # 2. Chercher les FONCTIONS
            fonctions_trouvees = [
                name
                for name, obj in inspect.getmembers(module, inspect.isfunction)
                if getattr(obj, "__module__", "") == module.__name__
                and name not in excluded
            ]
            print(f"📋 Fonctions trouvées: {len(fonctions_trouvees)}")
            for name in fonctions_trouvees:
                print(f"   • {name}")

            # Construire la map nom->callable pour l'interface
            self.functions_map = {}
            self.classes_map = {}

            # Ajouter les classes
            for name in classes_trouvees:
                obj = getattr(module, name, None)
                if obj is not None:
                    self.classes_map[name] = obj
                    print(f"✅ Classe disponible: {name}")

            # Ajouter les fonctions
            for name in fonctions_trouvees:
                obj = getattr(module, name, None)
                if callable(obj):
                    self.functions_map[name] = obj
                    print(f"✅ Fonction disponible: {name}")

            # Retourner tout ce qui a été trouvé
            fonctions_disponibles = list(self.functions_map.keys()) + list(
                self.classes_map.keys()
            )
            if not fonctions_disponibles:
                print("⚠️  Aucune classe ou fonction compatible trouvée!")
            return fonctions_disponibles

        except Exception as e:
            print(f"❌ Erreur chargement: {str(e)}")
            import traceback

            traceback.print_exc()
            return []

    def setup_ui(self):
        """Interface TRÈS SIMPLE"""
        self.setWindowTitle("🏗️ Générateur Kiosque - Ultra Simple")
        self.resize(800, 700)
        self.setMinimumSize(600, 400)

        # Utiliser un scroll area pour éviter le chevauchement des contrôles
        main_layout = QtGui.QVBoxLayout()
        scroll = QtGui.QScrollArea()
        scroll.setWidgetResizable(True)
        content = QtGui.QWidget()
        layout = QtGui.QVBoxLayout(content)

        # ============================================
        # 1. STATUT
        # ============================================
        if self.fonctions_chargees:
            label_statut = QtGui.QLabel(
                f"✅ Script chargé: {len(self.fonctions_chargees)} fonctions disponibles"
            )
            label_statut.setStyleSheet(
                """
                background-color: #27ae60;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            """
            )
        else:
            label_statut = QtGui.QLabel(
                "❌ Aucune fonction chargée - Vérifiez le chemin"
            )
            label_statut.setStyleSheet(
                """
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            """
            )

        layout.addWidget(label_statut)

        # Bouton pour choisir le script
        btn_choose = QtGui.QPushButton("📂 Choisir un script .py")
        btn_choose.clicked.connect(self.choisir_script)
        layout.addWidget(btn_choose)

        # ============================================
        # 2. PARAMÈTRES SIMPLES
        # ============================================
        group_params = QtGui.QGroupBox("📏 Paramètres Rapides")
        layout_params = QtGui.QGridLayout()

        # Quelques paramètres essentiels
        params = [
            ("Rayon pétales (mm):", 2200, "rayon"),
            ("Espacement (mm):", 1000, "espace"),
            ("Hauteur (mm):", 2200, "haut"),
            ("Hauteur Dôme (mm):", 3500, "hauteur_dome"),
            ("Mistral:", "100 km/h", "mistral"),
        ]

        self.controles = {}

        for i, (label, valeur, nom) in enumerate(params):
            lbl = QtGui.QLabel(label)
            layout_params.addWidget(lbl, i, 0)

            if nom == "mistral":
                combo = QtGui.QComboBox()
                combo.addItems(["100 km/h", "130 km/h"])
                self.controles[nom] = combo
                layout_params.addWidget(combo, i, 1)
            else:
                spin = QtGui.QSpinBox()
                # Set a larger default range and allow the dome height control
                if nom == "hauteur_dome":
                    spin.setRange(500, 10000)
                    spin.setValue(valeur)
                else:
                    spin.setRange(500, 5000)
                    spin.setValue(valeur)
                self.controles[nom] = spin
                layout_params.addWidget(spin, i, 1)

        group_params.setLayout(layout_params)
        layout.addWidget(group_params)

        # ============================================
        # 2.5 PRESETS & OPTIMISATION (if config available)
        # ============================================
        if CONFIG_AVAILABLE:
            group_presets = QtGui.QGroupBox("🎯 Preset & Optimisation")
            layout_presets = QtGui.QVBoxLayout()

            # Combo preset
            layout_preset_row = QtGui.QHBoxLayout()
            layout_preset_row.addWidget(QtGui.QLabel("Sélectionner preset:"))
            combo_preset = QtGui.QComboBox()
            combo_preset.addItems(list(PRESETS.keys()))
            combo_preset.currentIndexChanged.connect(
                lambda: self._apply_preset(combo_preset.currentText())
            )
            self.controles["preset"] = combo_preset
            layout_preset_row.addWidget(combo_preset)
            layout_presets.addLayout(layout_preset_row)

            # Paramètres secondaires (affichage)
            self.label_secondary = QtGui.QLabel(
                "Paramètres secondaires calculés: [En attente de sélection]"
            )
            self.label_secondary.setStyleSheet(
                "background-color: #ecf0f1; padding: 8px; border-radius: 3px;"
            )
            layout_presets.addWidget(self.label_secondary)

            # Estimation coûts
            self.label_cost = QtGui.QLabel("Estimation coûts: [En attente de calcul]")
            self.label_cost.setStyleSheet(
                "background-color: #d5f4e6; padding: 8px; border-radius: 3px;"
            )
            layout_presets.addWidget(self.label_cost)

            group_presets.setLayout(layout_presets)
            layout.addWidget(group_presets)

        # ============================================
        # 2.6 OPTIONS MODULAIRES (Retrofits)
        # ============================================
        if RETROFITS_AVAILABLE:
            group_retrofits = QtGui.QGroupBox("🔧 Options Modulaires")
            layout_retrofits = QtGui.QVBoxLayout()

            self.retrofit_checkboxes = {}
            for retrofit_name, retrofit_info in RETROFIT_OPTIONS.items():
                checkbox = QtGui.QCheckBox(retrofit_info["label"])
                checkbox.setToolTip(retrofit_info["description"])
                self.retrofit_checkboxes[retrofit_name] = checkbox
                self.selected_retrofits[retrofit_name] = False
                checkbox.stateChanged.connect(
                    lambda state, name=retrofit_name: self._update_retrofit_selection(
                        name, state
                    )
                )
                layout_retrofits.addWidget(checkbox)

            group_retrofits.setLayout(layout_retrofits)
            layout.addWidget(group_retrofits)

        # ============================================
        # 3. BOUTONS DE GÉNÉRATION
        # ============================================
        group_actions = QtGui.QGroupBox("🚀 Génération")
        layout_actions = QtGui.QVBoxLayout()

        # Bouton 1: Chercher et exécuter n'importe quelle fonction
        self.btn_magique = QtGui.QPushButton("✨ GÉNÉRER AUTOMATIQUEMENT (Recommandé)")
        self.btn_magique.setStyleSheet(
            """
            QPushButton {
                background-color: #9b59b6;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 12px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """
        )
        self.btn_magique.clicked.connect(self.generer_magique)
        self.btn_magique.setEnabled(
            bool(self.fonctions_chargees)
        )  # Enable if functions loaded
        layout_actions.addWidget(self.btn_magique)

        # Boutons spécifiques
        frame_boutons = QtGui.QFrame()
        frame_boutons.setMinimumHeight(60)
        layout_boutons_spec = QtGui.QHBoxLayout()
        layout_boutons_spec.setSpacing(10)  # Add spacing between buttons

        self.btn_standard = QtGui.QPushButton("🏗️ Standard")
        self.btn_standard.setMinimumHeight(45)
        self.btn_standard.setMinimumWidth(150)
        self.btn_standard.clicked.connect(self.generer_standard)
        self.btn_standard.setEnabled(bool(self.fonctions_chargees))
        layout_boutons_spec.addWidget(self.btn_standard)

        self.btn_plots = QtGui.QPushButton("🏗️ Avec Plots")
        self.btn_plots.setMinimumHeight(45)
        self.btn_plots.setMinimumWidth(150)
        self.btn_plots.clicked.connect(self.generer_plots)
        self.btn_plots.setEnabled(bool(self.fonctions_chargees))
        layout_boutons_spec.addWidget(self.btn_plots)

        frame_boutons.setLayout(layout_boutons_spec)
        layout_actions.addWidget(frame_boutons)

        # Bouton tester
        self.btn_tester = QtGui.QPushButton("🔍 Montrer les fonctions")
        self.btn_tester.clicked.connect(self.montrer_fonctions)
        layout_actions.addWidget(self.btn_tester)

        group_actions.setLayout(layout_actions)
        layout.addWidget(group_actions)

        # ============================================
        # 4. MESSAGE
        # ============================================
        self.label_message = QtGui.QLabel(
            "Cliquez sur 'GÉNÉRER AUTOMATIQUEMENT' pour commencer"
        )
        self.label_message.setStyleSheet(
            """
            background-color: #f1c40f;
            padding: 10px;
            border-radius: 5px;
            font-weight: bold;
        """
        )
        layout.addWidget(self.label_message)

        # Zone de logs
        self.log_area = QtGui.QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setFixedHeight(100)
        layout.addWidget(self.log_area)
        # ============================================
        # 5. BOUTON FERMER
        # ============================================
        btn_fermer = QtGui.QPushButton("❌ Fermer")
        btn_fermer.clicked.connect(self.close)
        layout.addWidget(btn_fermer)

        self.setLayout(layout)

        # ============================================
        # 5. PARAMÈTRES STRUCTURELS + ACTIONS
        # ============================================
        group_struct = QtGui.QGroupBox("⚙️ Paramètres Structurels & Matériaux")
        layout_struct = QtGui.QGridLayout()

        # Matériau
        layout_struct.addWidget(QtGui.QLabel("Matériau principal:"), 0, 0)
        combo_mat = QtGui.QComboBox()
        combo_mat.addItems(["Acier galvanisé (permanent)", "Bambou (temporaire)"])
        self.controles["material"] = combo_mat
        layout_struct.addWidget(combo_mat, 0, 1)

        # Vitesse vent (km/h)
        layout_struct.addWidget(QtGui.QLabel("Vitesse vent (km/h):"), 1, 0)
        spin_wind = QtGui.QSpinBox()
        spin_wind.setRange(0, 300)
        spin_wind.setValue(100)
        self.controles["wind_speed"] = spin_wind
        layout_struct.addWidget(spin_wind, 1, 1)

        # Facteur de sécurité
        layout_struct.addWidget(QtGui.QLabel("Facteur de sécurité:"), 2, 0)
        spin_sf = QtGui.QDoubleSpinBox()
        spin_sf.setRange(1.0, 3.0)
        spin_sf.setSingleStep(0.1)
        spin_sf.setValue(1.3)
        self.controles["safety_factor"] = spin_sf
        layout_struct.addWidget(spin_sf, 2, 1)

        group_struct.setLayout(layout_struct)
        layout.addWidget(group_struct)

        # ============================================
        # 6. BOUTONS SUPPLÉMENTAIRES
        # ============================================
        frame_actions2 = QtGui.QFrame()
        layout_actions2 = QtGui.QHBoxLayout()

        self.btn_generate_params = QtGui.QPushButton("🔧 Générer avec paramètres")
        self.btn_generate_params.setStyleSheet(
            "background-color: #2980b9; color: white; padding:8px;"
        )
        self.btn_generate_params.clicked.connect(self.generer_avec_parametres)
        layout_actions2.addWidget(self.btn_generate_params)

        self.btn_advice = QtGui.QPushButton("💡 Conseil dimensionnement")
        self.btn_advice.clicked.connect(self.montrer_conseil)
        layout_actions2.addWidget(self.btn_advice)

        frame_actions2.setLayout(layout_actions2)
        layout.addWidget(frame_actions2)

        # Bouton fermer
        btn_fermer = QtGui.QPushButton("❌ Fermer")
        btn_fermer.clicked.connect(self.close)
        layout.addWidget(btn_fermer)

        # Placer le content dans le scroll area
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

    def montrer_fonctions(self):
        """Montre toutes les classes et fonctions disponibles"""
        msg = ""

        # Afficher les classes
        if hasattr(self, "classes_map") and self.classes_map:
            toutes_classes = sorted(self.classes_map.keys())
            msg += f"Classes disponibles ({len(toutes_classes)}):\n"
            msg += "\n".join(f"  - {c}" for c in toutes_classes)
            msg += "\n\n"

        # Afficher les fonctions
        if hasattr(self, "functions_map") and self.functions_map:
            toutes_fonctions = sorted(self.functions_map.keys())
            msg += f"Fonctions disponibles ({len(toutes_fonctions)}):\n"
            msg += "\n".join(f"  - {f}" for f in toutes_fonctions)
        else:
            msg += "Aucune fonction disponible"

        if msg:
            QtGui.QMessageBox.information(self, "Classes et Fonctions", msg)
        else:
            QtGui.QMessageBox.warning(
                self, "Rien trouvé", "Aucune classe ou fonction disponible."
            )

    def generer_magique(self):
        """Essaie TOUTES les classes et fonctions jusqu'à ce qu'une marche"""
        try:
            self.label_message.setText(
                "🔍 Recherche d'une classe ou fonction qui marche..."
            )

            # 1. Essayer les CLASSES d'abord (plus probables)
            classes_a_tester = []
            if hasattr(self, "classes_map") and self.classes_map:
                for nom in self.classes_map.keys():
                    classes_a_tester.append(nom)

            # 2. Essayer les FONCTIONS (si classes ne marchent pas)
            fonctions_a_tester = []
            if hasattr(self, "functions_map") and self.functions_map:
                for nom in self.functions_map.keys():
                    if any(
                        mot in nom.lower() for mot in ["kiosque", "creer", "generer"]
                    ):
                        fonctions_a_tester.append(nom)

            print(
                f"🔧 {len(classes_a_tester)} classes et {len(fonctions_a_tester)} fonctions à tester"
            )

            # Tester les classes d'abord
            for nom_classe in classes_a_tester:
                try:
                    print(f"🧪 Test de classe: {nom_classe}")
                    doc_name = f"Test_{nom_classe}"
                    App.newDocument(doc_name)

                    classe = self.classes_map.get(nom_classe)
                    if classe is None:
                        raise RuntimeError(f"Classe {nom_classe} introuvable")

                    # Instancier et appeler generer_kiosque_complet_avec_plots
                    instance = classe()
                    if hasattr(instance, "generer_kiosque_complet_avec_plots"):
                        hauteur = (
                            int(self.controles.get("hauteur_dome").value())
                            if "hauteur_dome" in self.controles
                            else 3500
                        )
                        instance.config["hauteur_dome"] = hauteur
                        instance.generer_kiosque_complet_avec_plots()
                    elif hasattr(instance, "generer_kiosque"):
                        instance.generer_kiosque()
                    else:
                        raise RuntimeError(
                            f"Classe {nom_classe} n'a pas de méthode generer_kiosque"
                        )

                    print(f"✅ SUCCÈS avec classe: {nom_classe}")

                    # Zoom
                    if hasattr(Gui, "ActiveDocument") and Gui.ActiveDocument:
                        Gui.ActiveDocument.ActiveView.viewIsometric()
                        Gui.ActiveDocument.ActiveView.fitAll()

                    self.label_message.setText(f"✅ Réussi avec classe: {nom_classe}")
                    self._append_log(f"✅ Génération réussie avec {nom_classe}")
                    return

                except Exception as e:
                    print(f"❌ Échec classe {nom_classe}: {e}")
                    continue

            # Tester les fonctions ensuite
            for nom_fonction in fonctions_a_tester:
                try:
                    print(f"🧪 Test de fonction: {nom_fonction}")
                    doc_name = f"Test_{nom_fonction}"
                    App.newDocument(doc_name)

                    func = self.functions_map.get(nom_fonction)
                    if func is None:
                        raise RuntimeError("Fonction introuvable dans le module chargé")
                    self._call_with_dome_height(func, nom_fonction)
                    print(f"✅ SUCCÈS avec fonction: {nom_fonction}")

                    # Zoom
                    if hasattr(Gui, "ActiveDocument") and Gui.ActiveDocument:
                        Gui.ActiveDocument.ActiveView.viewIsometric()
                        Gui.ActiveDocument.ActiveView.fitAll()

                    self.label_message.setText(f"✅ Réussi avec: {nom_fonction}")
                    self._append_log(f"✅ Génération réussie avec {nom_fonction}")
                    return

                except Exception as e:
                    print(f"❌ Échec fonction {nom_fonction}: {e}")
                    continue

            # Si on arrive ici, rien n'a marché
            QtGui.QMessageBox.warning(
                self,
                "Aucune classe ou fonction compatible",
                "Aucune classe ou fonction n'a pu générer le kiosque.",
            )
            self.label_message.setText("❌ Aucune classe ou fonction n'a fonctionné")
            # Rien n'a fonctionné
            # (Le message ci-dessus informe déjà l'utilisateur)

        except Exception as e:
            self.label_message.setText(f"❌ Erreur: {str(e)}")
            print(f"Erreur génération magique: {e}")
            QtGui.QMessageBox.critical(self, "Erreur", f"Erreur:\n{str(e)}")

    def generer_standard(self):
        """Génère via la classe si disponible, sinon essaie fonctions standard."""
        # Essayer classe d'abord
        try:
            if hasattr(self, "classes_map") and self.classes_map:
                # Prendre la première classe trouvée (ex: KiosqueTrefleFonctionnel)
                nom_classe = sorted(self.classes_map.keys())[0]
                classe = self.classes_map[nom_classe]
                instance = classe()
                # Appliquer hauteur dôme si présente
                if "hauteur_dome" in getattr(self, "controles", {}):
                    try:
                        hd = int(self.controles["hauteur_dome"].value())
                        instance.config["hauteur_dome"] = hd
                    except Exception:
                        pass
                # Appeler la méthode standard
                if hasattr(instance, "generer_kiosque"):
                    App.newDocument("Kiosque_Standard")
                    instance.generer_kiosque()
                    return
                if hasattr(instance, "assembler_4_petales"):
                    App.newDocument("Kiosque_Standard")
                    instance.assembler_4_petales()
                    return
        except Exception:
            pass

        # Sinon essayer les fonctions libres
        self.essayer_fonctions(
            ["creer_kiosque_fonctionnel", "creer_kiosque", "generer_kiosque"]
        )

    def generer_plots(self):
        """Génère via la classe avec plots si disponible, sinon fonctions."""
        # Essayer classe d'abord
        try:
            if hasattr(self, "classes_map") and self.classes_map:
                nom_classe = sorted(self.classes_map.keys())[0]
                classe = self.classes_map[nom_classe]
                instance = classe()
                if "hauteur_dome" in getattr(self, "controles", {}):
                    try:
                        hd = int(self.controles["hauteur_dome"].value())
                        instance.config["hauteur_dome"] = hd
                    except Exception:
                        pass
                if hasattr(instance, "generer_kiosque_complet_avec_plots"):
                    App.newDocument("Kiosque_Plots")
                    instance.generer_kiosque_complet_avec_plots()
                    return
        except Exception:
            pass

        # Sinon essayer les fonctions libres
        self.essayer_fonctions(
            [
                "creer_kiosque_avec_plots",
                "creer_kiosque_complet",
                "generer_kiosque_complet",
            ]
        )

    def _call_with_dome_height(self, func, nom_fonction):
        """Appelle `func` en appliquant la valeur de `hauteur_dome` via la classe si possible.

        Logique : si le module chargé contient `KiosqueTrefleFonctionnel`, on crée une instance,
        on fixe `config['hauteur_dome']` avec la valeur UI, puis on appelle la méthode la plus
        appropriée (généralement `generer_kiosque_complet_avec_plots` pour les variantes avec plots,
        ou `assembler_4_petales` / `generer_*` sinon). Sinon on appelle la fonction directe.
        """
        try:
            hauteur = None
            if "hauteur_dome" in getattr(self, "controles", {}):
                try:
                    hauteur = int(self.controles["hauteur_dome"].value())
                except Exception:
                    hauteur = None

            # Si la classe est disponible dans le module chargé, privilégier son usage
            if hasattr(self, "module_loaded") and hasattr(
                self.module_loaded, "KiosqueTrefleFonctionnel"
            ):
                Kclass = getattr(self.module_loaded, "KiosqueTrefleFonctionnel")
                try:
                    instance = Kclass()
                    if hauteur is not None:
                        try:
                            instance.config["hauteur_dome"] = hauteur
                            _ = instance.config["hauteur_dome"]
                            self._append_log(f"Hauteur dôme appliquée: {hauteur} mm")
                        except Exception:
                            pass

                    # Choisir la méthode la plus adaptée
                    name = nom_fonction.lower() if nom_fonction else ""
                    if "plot" in name or "plots" in name or "complet" in name:
                        if hasattr(instance, "generer_kiosque_complet_avec_plots"):
                            instance.generer_kiosque_complet_avec_plots()
                            return
                    if "fonctionnel" in name or "original" in name:
                        if hasattr(instance, "assembler_4_petales"):
                            instance.assembler_4_petales()
                            return

                    # Fallback: essayer d'appeler une méthode générique si existante
                    if hasattr(instance, "generer_kiosque_complet_avec_plots"):
                        instance.generer_kiosque_complet_avec_plots()
                        return
                except Exception as e:
                    print(f"⚠️  Échec appel via classe: {e}")
                    # si échec, on continue et tente l'appel direct

            # Appel direct si rien d'autre
            func()
        except Exception as e:
            print(f"❌ Erreur lors de l'appel de {nom_fonction}: {e}")
            import traceback

            traceback.print_exc()

    def essayer_fonctions(self, noms_fonctions):
        """Essaie une liste de fonctions"""
        for nom in noms_fonctions:
            func = None
            if hasattr(self, "functions_map") and nom in self.functions_map:
                func = self.functions_map[nom]
            if func and callable(func):
                try:
                    print(f"🔧 Appel de: {nom}")
                    self.label_message.setText(f"🔄 Appel de {nom}...")
                    App.newDocument(f"Kiosque_{nom}")
                    # Call function while applying dome height if possible
                    self._call_with_dome_height(func, nom)
                    self.label_message.setText(f"✅ Réussi avec {nom}")
                    if hasattr(Gui, "ActiveDocument") and Gui.ActiveDocument:
                        Gui.ActiveDocument.ActiveView.viewIsometric()
                        Gui.ActiveDocument.ActiveView.fitAll()
                    QtGui.QMessageBox.information(
                        self, "Succès", f"Fonction {nom} a réussi!"
                    )
                    return
                except Exception as e:
                    print(f"❌ {nom} échoué: {e}")
                    try:
                        App.closeDocument(f"Kiosque_{nom}")
                    except Exception:
                        pass
                    continue

        QtGui.QMessageBox.warning(
            self,
            "Fonctions non trouvées",
            f"Aucune de ces fonctions n'a marché: {', '.join(noms_fonctions)}\n"
            f"Essayez 'GÉNÉRER AUTOMATIQUEMENT'.",
        )


# ============================================================================
# FONCTIONS UTILES
# ============================================================================


def trouver_script_manuellement():
    """Vous aide à trouver votre script"""
    print("\n" + "=" * 60)
    print("🔍 AIDE POUR TROUVER VOTRE SCRIPT")
    print("=" * 60)

    # Demander le fichier
    fichier, _ = QtGui.QFileDialog.getOpenFileName(
        None,
        "Montrez-moi votre fichier kiosque_trefle_4petales_dome22.py",
        os.path.expanduser("~"),
        "Python Files (*.py)",
    )

    if fichier:
        print(f"✅ Vous avez sélectionné: {fichier}")

        # Créer et ouvrir l'interface avec ce chemin
        interface = InterfaceUltraSimple(fichier)
        interface.exec_()

        return fichier
    else:
        print("❌ Aucun fichier sélectionné")
        return None


def lancer_interface_fixe():
    """Lance l'interface avec chemin fixe"""
    # MODIFIEZ CE CHEMIN !!!
    VOTRE_VRAI_CHEMIN = r"C:\Users\VotreNom\Documents\FreeCAD\SCRIPTS_PARAMETRIQUES\kiosque_trefle_4petales_dome22.py"

    interface = InterfaceUltraSimple(VOTRE_VRAI_CHEMIN)
    interface.exec_()


# === NOUVEAUX MÉTHODES POUR LA SÉLECTION DE SCRIPT ET LOGGING ===
def _append_log(self, texte):
    try:
        if hasattr(self, "log_area"):
            self.log_area.append(texte)
    except Exception:
        pass


def choisir_script(self):
    fichier, _ = QtGui.QFileDialog.getOpenFileName(
        None,
        "Sélectionnez votre script kiosque .py",
        os.path.expanduser("~"),
        "Python Files (*.py)",
    )
    if fichier:
        self.chemin_script = fichier
        self.label_message.setText(f"🔁 Chargement: {os.path.basename(fichier)}")
        # Recharger le module
        fonctions = self.charger_script_explicitement()
        self.fonctions_chargees = fonctions
        # Mettre à jour boutons
        try:
            self.btn_standard.setEnabled(bool(self.fonctions_chargees))
            self.btn_plots.setEnabled(bool(self.fonctions_chargees))
            self.btn_magique.setEnabled(
                bool(self.fonctions_chargees)
            )  # Enable magique button
        except Exception:
            pass
        _append_log(self, f"Chargé: {fichier}")


# Attacher les nouvelles méthodes à la classe
setattr(InterfaceUltraSimple, "_append_log", _append_log)
setattr(InterfaceUltraSimple, "choisir_script", choisir_script)


def _apply_preset(self, preset_name):
    """Applique un preset (Permanent/Temporaire) et met à jour les paramètres."""
    if not CONFIG_AVAILABLE or preset_name not in PRESETS:
        return

    preset = PRESETS[preset_name]
    try:
        # Appliquer les paramètres du preset aux contrôles
        if "material" in self.controles:
            combo_text = (
                "Acier galvanisé (permanent)"
                if "Acier" in preset.get("material", "")
                else "Bambou (temporaire)"
            )
            for i in range(self.controles["material"].count()):
                if combo_text in self.controles["material"].itemText(i):
                    self.controles["material"].setCurrentIndex(i)
                    break

        if "wind_speed" in self.controles:
            self.controles["wind_speed"].setValue(preset.get("wind", 100))

        if "safety_factor" in self.controles:
            self.controles["safety_factor"].setValue(preset.get("safety_factor", 1.25))

        # Calculer paramètres secondaires
        rayon = (
            int(self.controles.get("rayon").value())
            if "rayon" in self.controles
            else 2200
        )
        hauteur = (
            int(self.controles.get("haut").value())
            if "haut" in self.controles
            else 2200
        )
        espace = (
            int(self.controles.get("espace").value())
            if "espace" in self.controles
            else 1000
        )
        hauteur_dome = (
            int(self.controles.get("hauteur_dome").value())
            if "hauteur_dome" in self.controles
            else 3500
        )
        wind = self.controles.get("wind_speed").value()
        material = (
            self.controles.get("material").currentText()
            if "material" in self.controles
            else "Acier"
        )
        sf = (
            self.controles.get("safety_factor").value()
            if "safety_factor" in self.controles
            else 1.25
        )

        # Calcul avec config
        self.secondary_params = calculate_secondary_params(
            rayon, hauteur, espace, hauteur_dome, material, wind, sf
        )
        self.cost_estimate = estimate_costs(rayon, hauteur, material, "plots", 50)

        # Mettre à jour l'affichage
        secondary_text = (
            f"Ø Anneau: {self.secondary_params.get('diametre_anneau_mm')}mm | "
            f"Montants: {self.secondary_params.get('n_montants')} | "
            f"Tubes: Ø{self.secondary_params.get('tube_diametre_mm')}mm | "
            f"Ancrage: {self.secondary_params.get('ancrage_profondeur_mm')}mm"
        )
        if hasattr(self, "label_secondary"):
            self.label_secondary.setText(f"✓ {secondary_text}")

        cost_text = (
            f"Acier: {self.cost_estimate.get('acier_kg')}kg | "
            f"Béton: {self.cost_estimate.get('beton_tonnes')}t | "
            f"Coût estimé: ${self.cost_estimate.get('cout_usd_estime')}"
        )
        if hasattr(self, "label_cost"):
            self.label_cost.setText(f"💰 {cost_text}")

        self._append_log(
            f"✓ Preset '{preset_name}' appliqué - Params secondaires calculés"
        )

    except Exception as e:
        print(f"❌ Erreur apply_preset: {e}")
        self._append_log(f"❌ Erreur preset: {e}")


def _update_retrofit_selection(self, retrofit_name, state):
    """Enregistre la sélection d'un retrofit."""
    self.selected_retrofits[retrofit_name] = state != 0
    retrofit_info = RETROFIT_OPTIONS.get(retrofit_name, {})
    status = "✓ Ajouté" if state != 0 else "✗ Retiré"
    self._append_log(f"{status}: {retrofit_info.get('label', retrofit_name)}")


# Attacher les nouvelles méthodes à la classe
setattr(InterfaceUltraSimple, "_append_log", _append_log)
setattr(InterfaceUltraSimple, "choisir_script", choisir_script)


def generer_avec_parametres(self):
    """Collecte paramètres clés et génère le kiosque via la classe si disponible."""
    try:
        # Récupérer paramètres clefs
        rayon = (
            int(self.controles.get("rayon").value())
            if "rayon" in self.controles
            else None
        )
        espace = (
            int(self.controles.get("espace").value())
            if "espace" in self.controles
            else None
        )
        hauteur_montant = (
            int(self.controles.get("haut").value())
            if "haut" in self.controles
            else None
        )
        hauteur_dome = (
            int(self.controles.get("hauteur_dome").value())
            if "hauteur_dome" in self.controles
            else None
        )
        material = (
            self.controles.get("material").currentText()
            if "material" in self.controles
            else None
        )
        wind = (
            int(self.controles.get("wind_speed").value())
            if "wind_speed" in self.controles
            else None
        )
        sf = (
            float(self.controles.get("safety_factor").value())
            if "safety_factor" in self.controles
            else None
        )

        msg = (
            f"Paramètres: rayon={rayon}, espace={espace}, hauteur_montant={hauteur_montant}, "
            f"hauteur_dome={hauteur_dome}, mat={material}, vent={wind}, FS={sf}"
        )
        self._append_log(msg)

        # Si la classe est disponible, l'utiliser
        if hasattr(self, "module_loaded") and hasattr(
            self.module_loaded, "KiosqueTrefleFonctionnel"
        ):
            Kclass = getattr(self.module_loaded, "KiosqueTrefleFonctionnel")
            instance = Kclass()
            # Appliquer paramètres au config si présents
            try:
                if rayon is not None:
                    instance.config["rayon_petale"] = rayon
                if hauteur_montant is not None:
                    instance.config["hauteur_petale"] = hauteur_montant
                if espace is not None:
                    instance.config["rayon_rosaire"] = espace
                if hauteur_dome is not None:
                    instance.config["hauteur_dome"] = hauteur_dome
                # stocker meta params
                instance.config["material"] = material
                instance.config["wind_speed"] = wind
                instance.config["safety_factor"] = sf
            except Exception as e:
                print(f"⚠️  Impossible d'appliquer certains paramètres: {e}")

            # Appel principal
            try:
                instance.generer_kiosque_complet_avec_plots()
                self._append_log("Génération terminée via KiosqueTrefleFonctionnel")
            except Exception as e:
                print(f"❌ Erreur génération: {e}")
                import traceback

                traceback.print_exc()
                QtGui.QMessageBox.critical(self, "Erreur génération", str(e))
        else:
            # Si pas de classe, essayer d'appeler une fonction nommée
            if "creer_kiosque_avec_plots" in getattr(self, "functions_map", {}):
                func = self.functions_map["creer_kiosque_avec_plots"]
                try:
                    self._call_with_dome_height(func, "creer_kiosque_avec_plots")
                except Exception as e:
                    QtGui.QMessageBox.critical(self, "Erreur génération", str(e))
            else:
                QtGui.QMessageBox.warning(
                    self,
                    "Pas de cible",
                    "Aucune classe ou fonction compatible trouvée dans le script chargé.",
                )

    except Exception as e:
        print(f"❌ Erreur generer_avec_parametres: {e}")
        import traceback

        traceback.print_exc()


def montrer_conseil(self):
    """Affiche un conseil simple de dimensionnement basé sur vent/matériau/FS."""
    try:
        wind = (
            int(self.controles.get("wind_speed").value())
            if "wind_speed" in self.controles
            else 100
        )
        material = (
            self.controles.get("material").currentText()
            if "material" in self.controles
            else "Acier"
        )
        sf = (
            float(self.controles.get("safety_factor").value())
            if "safety_factor" in self.controles
            else 1.3
        )

        # Calcul heuristique simple
        factor = 1.0 + max(0, (wind - 100) / 200.0)  # augmente avec le vent
        if material.lower().startswith("bambou"):
            sf_rec = max(1.5, sf)
            note = "Bambou = solution temporaire; préconiser FS plus élevé et surveillance."
        else:
            sf_rec = max(1.25, sf)
            note = (
                "Acier galvanisé recommandé pour usage permanent; FS modéré acceptable."
            )

        # Recommandation sur plots
        base_increase = factor
        rec_plot_pct = int((base_increase - 1.0) * 100)
        rec_text = (
            f"Conseil rapide:\n\n- Vent: {wind} km/h => augmenter dimension plots d'environ {rec_plot_pct}%\n"
            f"- Facteur de sécurité recommandé: {sf_rec:.2f}\n- Matériau: {material}\n\n{note}\n\n"
            "Suggestions pratiques:\n"
            "• Pour vent >120 km/h augmenter profondeur d'enfouissement et volume béton (x1.3–2.0).\n"
            "• Pour bambou: préférez ancrages supplémentaires et inspection post-tempête.\n"
            "• Vérifier dimensionnement structurel par calculs normatifs pour votre site."
        )

        QtGui.QMessageBox.information(self, "Conseil dimensionnement", rec_text)
        self._append_log("Conseil affiché")
    except Exception as e:
        print(f"Erreur montrer_conseil: {e}")
        import traceback

        traceback.print_exc()


setattr(InterfaceUltraSimple, "generer_avec_parametres", generer_avec_parametres)
setattr(InterfaceUltraSimple, "montrer_conseil", montrer_conseil)

# ============================================================================
# COMMANDES SIMPLES
# ============================================================================

print("\n" + "=" * 60)
print("🎯 COMMANDES DISPONIBLES :")
print("=" * 60)
print("\n1. Pour chercher manuellement votre script:")
print("   >>> trouver_script_manuellement()")
print("\n2. Avec chemin fixe (modifiez le code d'abord):")
print("   >>> lancer_interface_fixe()")
print("\n" + "=" * 60)
print("📋 ÉTAPE IMPORTANTE:")
print("Ouvrez le fichier et MODIFIEZ LA LIGNE 14 avec votre vrai chemin!")
print("=" * 60)

# Si exécuté directement
if __name__ == "__main__":
    print("\n🔧 Lancement de l'aide pour trouver votre script...")
    trouver_script_manuellement()
