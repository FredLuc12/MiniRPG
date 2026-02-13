# L'Aventure du Donjon Perdu

**MiniRPG** - RPG complet en Python orienté objet (H3 HITEMA)

[![UML Diagramme](https://img.shields.io/badge/UML-Diagramme-blue)](https://lucid.app/lucidchart/36636b0c-b0e3-4840-8e63-c0fb93aea810/edit?viewport_loc=2559%2C1767%2C1830%2C840%2CHWEp-vi-RSFO&invitationId=inv_ea6a5471-27a2-4e21-8367-5dec53beea32)

## 🎮 **GAMEPLAY**

**Objectif** : Trouver la **Clé du Donjon** dans la Forêt, puis vaincre le **Gardien du Donjon** !

```
Village → Forêt (combats, coffres, clés) → Donjon (boss final)
   ↓              ↓                           ↓
Marchand    Loup/Bandit/Squelette     Champion + Gardien
Repos + Dialogue              Clé du Donjon → Victoire !
```

## **FONCTIONNALITÉS**

| **Système** | **Détails** |
|-------------|-------------|
| **Classes** | Guerrier(100PV), Mage(30PV+INT), Voleur(agilité) |
| **Combat** | Tour par tour interactif + 5 actions (Attaque/Compétence/Objet/Défendre/Fuir) |
| **Inventaire** | 10 slots (Potions, Épées, Armures) + équipement dynamique |
| **Statuts** | Poison, Bouclier, Étourdissement, Brûlure (gestion durée/tick) |
| **Zones** | Village(sûr), Forêt(dangereuse), Donjon(boss) |
| **Économie** | Or, marchand (3 items), loots combats |
| **Sauvegarde** | JSON complète (perso+jeu) + chargement |
| **Quête** | 3 étapes (Clé → Boss → Victoire) |

##**ARCHITECTURE (28 classes)**

```
    Hiérarchies POO :
├── Personnage (abstract) ← Guerrier, Mage, Voleur
├── Ennemi (abstract) ← LoupSauvage, Bandit, Squelette, ChampionCorrompu, GardienDonjon
├── Item (abstract) ← Weapon, Armor, Consumable
└── StatusEffect (abstract) ← Poison, Shield, Stun, Brulure

    Moteur principal :
├── Jeu ← Zones, Quête, Événements
├── Inventory (1→*)
├── Combat interactif (statuts+IA)
└── Sauvegarde (dataclasses JSON)
```

## **INSTALLATION & LANCEMENT**

```bash
# Prérequis : Python 3.8+
git clone <repo>
cd MiniRPG1
python main.py
```

**Lancement direct** :
```
1. Nouvelle partie / Charger sauvegarde
2. Nom + Classe (Guerrier/Mage/Voleur)
3. Explorer ! (1=Village, 2=Forêt, 3=Donjon)
```

## **COMMANDES EN JEU**

```
MENU PRINCIPAL :
1 Village   2 Forêt   3 Donjon
4 Status    5 Sauvegarder   6 Charger
0 Quitter

COMBAT :
1 Attaquer | 2 Compétence | 3 Objet
4 Défendre | 5 Fuir
```

## **STATISTIQUES DU PROJET**

| **Métrique** | **Valeur** |
|--------------|------------|
| **Lignes de code** | ~4k |
| **Classes** | 28 (4 abstraites) |
| **Fichiers** | main.py (monolithique) |
| **Complexité** | POO avancée (héritage, polymorphisme, propriétés) |
| **Temps dev** | 2 jours (debug intensif) |

## **TECH STACK**

```python
Python 3.12
dataclasses (sauvegarde JSON)
typing (List, Dict, Any)
Propriétés (@property attaque/defense)
Héritage multiple (Item/Personnage/Ennemi)
Gestion d'erreurs (try/except implicite)
```

## **COMPÉTENCES ACQUISES (H3 HITEMA)**

-  **POO avancée** : Héritage, polymorphisme, propriétés
- **Gestion état** : Statuts tickés/durées
- **Sérialisation** : JSON bidirectionnelle
- **Game loops** : Combat/exploration
- **Événements** : Système pondéré
- **CLI interactive** : input() non-bloquant

```

## **CRÉDITS**

**Auteur** : Étudiant H3 HITEMA (IT/DevOps)
**Debugging** : Perplexity AI (IA collaborative)
**Inspiration** : D&D, Epic RPG Discord

```
"Le Donjon Perdu attend son héros..."
```