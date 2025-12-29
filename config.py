"""
Configuration centralisée pour le générateur Kiosque Trèfle.
Contient presets, formules d'optimisation et constantes.
"""

# ============================================================================
# PRESETS (Permanent vs Temporaire)
# ============================================================================

PRESETS = {
    "Permanent (Acier)": {
        "material": "Acier galvanisé",
        "safety_factor": 1.25,
        "wind_speed": 100,
        "anchor_type": "isolated_plots",  # plots isolés espacés
        "cost_optimization": 50,
        "description": "Structure pérenne, acier galvanisé, ancrage robuste",
    },
    "Temporaire (Bambou)": {
        "material": "Bambou",
        "safety_factor": 1.5,
        "wind_speed": 80,
        "anchor_type": "continuous_semicircle",  # semi-cercles continus
        "cost_optimization": 70,
        "description": "Structure légère, bambou, ancrage économe",
    },
}

# ============================================================================
# FORMULES D'OPTIMISATION (paramètres secondaires)
# ============================================================================


def calculate_secondary_params(
    rayon, hauteur_montant, espace, hauteur_dome, material, wind_speed, sf
):
    """
    Calcule les paramètres secondaires (anneau, tubes, montants, ancrage)
    à partir des paramètres primaires.

    Args:
        rayon: rayon des pétales (mm)
        hauteur_montant: hauteur des montants (mm)
        espace: espacement entre pétales (mm)
        hauteur_dome: hauteur du dôme (mm)
        material: "Acier galvanisé" ou "Bambou"
        wind_speed: vitesse vent (km/h)
        sf: facteur de sécurité

    Returns:
        dict avec diamètre anneau, nb montants, diam tubes, profondeur ancrage
    """

    # Anneau central (clé de voûte) - fonction rayon et hauteur
    diametre_anneau = rayon * 0.4 + hauteur_dome * 0.2
    diametre_anneau = max(200, min(1000, diametre_anneau))  # limites raisonnables

    # Nombre de montants (stabilité circulaire)
    n_montants = max(4, int((2 * 3.14159 * rayon) / 400))  # 1 tous les ~400mm

    # Diamètre tubes (fonction vent, matériau, FS)
    tube_base = 60 if material == "Bambou" else 50  # bambou plus épais
    wind_factor = 1.0 + max(0, (wind_speed - 100) / 200.0)  # augmente avec vent
    tube_diam = tube_base * wind_factor * (sf / 1.25)  # normaliser à SF=1.25

    # Profondeur ancrage (~80% hauteur montant)
    ancrage_prof = hauteur_montant * 0.8

    # Espacement plots (si continu, vérifier si < 200mm)
    espacement_plots = (2 * 3.14159 * (rayon + 500)) / n_montants
    ancrage_mode = (
        "continuous_semicircle" if espacement_plots < 200 else "isolated_plots"
    )

    return {
        "diametre_anneau_mm": round(diametre_anneau, 1),
        "n_montants": int(n_montants),
        "tube_diametre_mm": round(tube_diam, 1),
        "ancrage_profondeur_mm": round(ancrage_prof, 1),
        "espacement_plots_mm": round(espacement_plots, 1),
        "ancrage_mode": ancrage_mode,
    }


def estimate_costs(rayon, hauteur_montant, material, ancrage_type, cost_optimization):
    """
    Estime les coûts matériaux basés sur géométrie et options.

    Args:
        cost_optimization: 0-100 (0=coût ignorer, 100=minimiser coûts)

    Returns:
        dict avec coûts estimés acier/béton/main d'œuvre
    """
    base_acier = rayon / 100.0 * hauteur_montant / 1000.0  # kg estimé
    base_beton = hauteur_montant * 0.5  # tonnes estimées

    if material == "Bambou":
        base_acier *= 0.3  # moins d'acier
        base_beton *= 0.7  # moins de béton

    # Facteur optimisation coûts
    if cost_optimization > 70:
        base_acier *= 0.85
        base_beton *= 0.8

    return {
        "acier_kg": round(base_acier, 1),
        "beton_tonnes": round(base_beton, 2),
        "cout_usd_estime": round((base_acier * 2 + base_beton * 50), 0),
    }


# ============================================================================
# CONSTANTES RETROFIT
# ============================================================================

RETROFIT_OPTIONS = {
    "sliding_panels": {
        "label": "Panneaux coulissants circulaires",
        "description": "Panneaux entre montants (composite/métal)",
        "materials": ["Composite", "Métal", "Bois"],
        "cost_multiplier": 1.2,
    },
    "dome_cladding": {
        "label": "Habillage dôme",
        "description": "Toile imperméable (lin-chanvre, polyester)",
        "materials": ["Lin-Chanvre", "Toile polyester", "Polycarbonate"],
        "cost_multiplier": 1.15,
    },
    "sliding_doors": {
        "label": "Portes coulissantes",
        "description": "Portes entre pétales (1-4)",
        "n_doors": [1, 2, 3, 4],
        "cost_multiplier": 1.25,
    },
    "removable_floor": {
        "label": "Plancher démontable",
        "description": "Plancher bois/composite amovible",
        "materials": ["Bois", "Composite"],
        "cost_multiplier": 1.18,
    },
    "open_stand": {
        "label": "Aménagement stand ouvert",
        "description": "Ouvre pétales pour commerce/exposition",
        "n_petals": [1, 2, 3, 4],
        "cost_multiplier": 0.95,  # économie de structure fermée
    },
}

# ============================================================================
# CONSTANTES SÉCURITÉ
# ============================================================================

SAFETY_LIMITS = {
    "wind_speed_max": 150,  # km/h
    "tube_diametre_min": 30,  # mm
    "tube_diametre_max": 200,  # mm
    "ancrage_profondeur_min": 600,  # mm
    "n_montants_min": 4,
    "n_montants_max": 12,
}
