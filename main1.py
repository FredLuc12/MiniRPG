import random
import json
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import os

# =========================
# EXTENSIONS OPTIONNELLES
# =========================

class NiveauDifficulte:
    """Gère les 3 niveaux de difficulté."""
    NIVEAUX = {
        "facile": {"pv_multi": 0.7, "degats_multi": 0.8, "or_multi": 1.5},
        "normal": {"pv_multi": 1.0, "degats_multi": 1.0, "or_multi": 1.0},
        "difficile": {"pv_multi": 1.5, "degats_multi": 1.3, "or_multi": 0.7}
    }
    
    @staticmethod
    def appliquer_stats(ennemi_base, niveau):
        """Modifie les stats de l'ennemi selon la difficulté."""
        multi = NiveauDifficulte.NIVEAUX[niveau]
        ennemi_base.pv = int(ennemi_base.pv * multi["pv_multi"])
        ennemi_base.defense = int(ennemi_base.defense * multi["pv_multi"])
        ennemi_base.force1 = int(getattr(ennemi_base, 'force1', 20) * multi["degats_multi"])
        return ennemi_base

class Marchand:
    """Système économique complet."""
    STOCK = {
        "Potion de soin": {"type": "Consumable", "prix": 20, "stock": 99, "valeur": 10},
        "Épée d'acier": {"type": "Weapon", "prix": 50, "stock": 5, "valeur": 25, "attack_bonus": 15},
        "Armure renforcée": {"type": "Armor", "prix": 40, "stock": 3, "valeur": 20, "defense_bonus": 10}
    }
    
    def __init__(self, niveau_difficulte="normal"):
        self.niveau = niveau_difficulte
        self.or_joueur = 0  # Sera setté par Jeu
    
    def ajuster_prix(self, prix_base):
        multi = {"facile": 0.8, "normal": 1.0, "difficile": 1.5}[self.niveau]
        return int(prix_base * multi)


# =========================
# Personnages et compétences
# =========================

class Personnage:
    def __init__(self, nom, type_, pv, pv_max, intelligence, agilite, competences, force1, force2, defense):
        self.nom = nom
        self.type = type_
        self.pv = pv
        self.pv_max = pv
        self.intelligence = intelligence
        self.agilite = agilite
        self.competences = competences      # liste de noms ou d’objets
        self.force1 = force1               # stat offensive principale (physique)
        self.force2 = force2               # stat offensive secondaire
        self.defense_base = defense        # défense de base (sans armure)
        self.statuts = []                  # liste de StatusEffect actifs

        # équipement
        self.weapon = None
        self.armor = None

        # inventaire limité à 10 slots
        self.inventory = Inventory(capacity=10)

    @property
    def defense(self):
        """Défense totale = base + armure."""
        bonus = self.armor.defense_bonus if self.armor else 0
        return self.defense_base + bonus

    @property
    def attaque(self):
        """Attaque totale = force1 + arme éventuelle."""
        bonus = self.weapon.attack_bonus if self.weapon else 0
        return self.force1 + bonus

    def equip_weapon(self, weapon):
        """Équipe 1 arme, applique son bonus via la propriété attaque."""
        if not isinstance(weapon, Weapon):
            print("Ce n'est pas une arme.")
            return
        if weapon not in self.inventory.items:
            print("L'arme doit être dans l'inventaire pour être équipée.")
            return
        self.weapon = weapon
        print(f"{self.nom} équipe {weapon.name} (+{weapon.attack_bonus} ATK).")

    def equip_armor(self, armor):
        """Équipe 1 armure, applique son bonus via la propriété defense."""
        if not isinstance(armor, Armor):
            print("Ce n'est pas une armure.")
            return
        if armor not in self.inventory.items:
            print("L'armure doit être dans l'inventaire pour être équipée.")
            return
        self.armor = armor
        bonuses = [f"+{armor.defense_bonus} DEF"]
        if armor.int_bonus:
            bonuses.append(f"+{armor.int_bonus} INT")
        print(f"{self.nom} équipe {armor.name} ({', '.join(bonuses)}).")


# =========================
# Items / Inventaire
# =========================

class Item:
    def __init__(self, name):
        self.name = name


class Weapon(Item):
    def __init__(self, name, attack_bonus=0, int_bonus=0):
        super().__init__(name)
        self.attack_bonus = attack_bonus
        self.int_bonus = int_bonus  # si tu veux des armes magiques


class Armor(Item):
    def __init__(self, name, defense_bonus=0, int_bonus=0):
        super().__init__(name)
        self.defense_bonus = defense_bonus
        self.int_bonus = int_bonus


class Consumable(Item):
    def __init__(self, name, effect):
        super().__init__(name)
        self.effect = effect  # fonction ou identifiant


class Inventory:
    def __init__(self, capacity=10):
        self.capacity = capacity
        self.items = []  # liste des objets

    def add_item(self, item):
        if len(self.items) >= self.capacity:
            print("Inventaire plein, impossible d'ajouter l'objet.")
            return False
        self.items.append(item)
        print(f"Objet ajouté à l'inventaire : {item.name}.")
        return True

    def remove_item(self, item):
        if item in self.items:
            self.items.remove(item)
            print(f"Objet retiré de l'inventaire : {item.name}.")
            return True
        print("Objet introuvable dans l'inventaire.")
        return False

    def has_item(self, item_name):
        return any(i.name == item_name for i in self.items)

    def get_item(self, item_name):
        for i in self.items:
            if i.name == item_name:
                return i
        return None


# =========================
# Compétences (mêmes qu’avant)
# =========================

class Competence:
    def __init__(self, nom, effet=None):
        self.nom = nom
        self.effet = effet


class CoupPuissant(Competence):
    def __init__(self):
        super().__init__("Coup puissant")


class Charge(Competence):
    def __init__(self):
        super().__init__("Charge")


class BouleDeFeu(Competence):
    def __init__(self):
        super().__init__("Boule de feu")


class Bouclier(Competence):
    def __init__(self):
        super().__init__("Bouclier")


class AttaqueSournoise(Competence):
    def __init__(self):
        super().__init__("Attaque sournoise")


class Esquive(Competence):
    def __init__(self):
        super().__init__("Esquive")


class ComboAttack(Competence):
    """Compétence combo : Attaque + Poison."""
    def __init__(self):
        super().__init__("Attaque empoisonnée")


class Guerrier(Personnage):
    def __init__(self, nom):
        competences = ["Coup puissant", "Charge"]
        super().__init__(
            nom=nom,
            type_="Guerrier",
            pv=100,
            pv_max=100,
            intelligence=40,
            agilite=50,
            competences=competences,
            force1=50,
            force2=60,
            defense=20,
        )


class Mage(Personnage):
    def __init__(self, nom):
        competences = ["Boule de feu", "Bouclier"]
        super().__init__(
            nom=nom,
            type_="Mage",
            pv=30,
            pv_max=100,
            intelligence=100,
            agilite=40,
            competences=competences,
            force1=20,
            force2=30,
            defense=10,
        )


class Voleur(Personnage):
    def __init__(self, nom):
        competences = ["Attaque sournoise", "Esquive"]
        super().__init__(
            nom=nom,
            type_="Voleur",
            pv=30,
            pv_max=100,
            intelligence=60,
            agilite=100,
            competences=competences,
            force1=30,
            force2=40,
            defense=15,
        )

# ==============
# Ennemis / boss
# ==============

class Ennemi:
    def __init__(self, nom, type_, pv, pv_max, difficulte, particularites, phase=1, defense=0, agilite=0):
        self.nom = nom
        self.type = type_              # "standard", "elite", "boss"
        self.pv = pv
        self.pv_max=100
        self.difficulte = difficulte   # 1, 2, 3 par exemple
        self.particularites = particularites  # liste de tags
        self.phase = phase
        self.defense = defense
        self.agilite = agilite
        self.statuts = []              # liste de StatusEffect actifs

    def mettre_a_jour_phase(self):
        """Hook pour le moteur de combat (boss à phases)."""
        if self.type == "boss" and hasattr(self, "pv_max") and self.pv <= self.pv_max // 2:
            if self.phase == 1:
                self.phase = 2
                print(f"{self.nom} entre en phase 2 !")

    def __str__(self):
        return f"{self.nom} ({self.type}, phase {self.phase})"


class LoupSauvage(Ennemi):
    def __init__(self, nom="Loup sauvage"):
        particularites = ["attaque_multiple", "rapide"]
        super().__init__(
            nom=nom,
            type_="standard",
            pv=50,
            pv_max=100,
            difficulte=1,
            particularites=particularites,
            phase=1,
            defense=5,
            agilite=30,
        )


class Bandit(Ennemi):
    def __init__(self, nom="Bandit"):
        particularites = ["vol_objets"]
        super().__init__(
            nom=nom,
            type_="standard",
            pv=60,
            pv_max=100,
            difficulte=1,
            particularites=particularites,
            phase=1,
            defense=8,
            agilite=20,
        )


class Squelette(Ennemi):
    def __init__(self, nom="Squelette"):
        particularites = ["resistant_physique"]
        super().__init__(
            nom=nom,
            type_="standard",
            pv=70,
            pv_max=100,
            difficulte=1,
            particularites=particularites,
            phase=1,
            defense=15,
            agilite=10,
        )


class ChampionCorrompu(Ennemi):
    def __init__(self, nom="Champion corrompu"):
        particularites = ["pv_eleves", "competence_speciale"]
        super().__init__(
            nom=nom,
            type_="elite",
            pv=150,
            pv_max=150,
            difficulte=2,
            particularites=particularites,
            phase=1,
            defense=20,
            agilite=15,
        )


class GardienDonjon(Ennemi):
    def __init__(self, nom="Gardien du donjon"):
        particularites = [
            "attaque_puissante",
            "resistant",
            "pv_eleves",
            "competence_speciale",
            "phase_multiple",
        ]
        super().__init__(
            nom=nom,
            type_="boss",
            pv=300,
            pv_max=300,
            difficulte=3,
            particularites=particularites,
            phase=1,
            defense=25,
            agilite=10,
        )
        self.pv_max = self.pv



# ===========================
# Système de statuts générique
# ===========================

class StatusEffect:
    """
    Statut générique : tout statut dérive de cette classe.
    trigger_moment : "start_turn", "on_hit", etc.
    duration : nombre de tours restants.
    """
    def __init__(self, nom, duration, trigger_moment):
        self.nom = nom
        self.duration = duration
        self.trigger_moment = trigger_moment

    def apply(self, target):
        """Appelé au moment de déclenchement (début de tour / impact...)."""
        pass

    def on_expire(self, target):
        """Nettoyage lors de l’expiration."""
        pass

    def tick(self, target):
        """
        Appelé à chaque tour pour gérer la durée.
        Retourne True si le statut est encore actif, False s’il expire.
        """
        self.duration -= 1
        if self.duration <= 0:
            self.on_expire(target)
            return False
        return True


class Poison(StatusEffect):
    def __init__(self, damage_per_turn=10, duration=3):
        super().__init__("Poison", duration, trigger_moment="start_turn")
        self.damage_per_turn = damage_per_turn

    def apply(self, target):
        target.pv -= self.damage_per_turn
        print(f"{target.nom} souffre du poison et perd {self.damage_per_turn} PV (reste {target.pv}).")


class Shield(StatusEffect):
    def __init__(self, shield_points=30, duration=3):
        super().__init__("Bouclier", duration, trigger_moment="on_hit")
        self.shield_points = shield_points

    def absorb_damage(self, target, damage):
        absorb = min(damage, self.shield_points)
        self.shield_points -= absorb
        damage_rest = damage - absorb
        print(f"Le bouclier absorbe {absorb} dégâts (reste {self.shield_points} points de bouclier).")
        if self.shield_points <= 0:
            self.duration = 0  # forcera l’expiration au prochain tick
        return damage_rest

    def on_expire(self, target):
        print(f"Le bouclier de {target.nom} se dissipe.")


class Stun(StatusEffect):
    def __init__(self, duration=1):
        super().__init__("Etourdissement", duration, trigger_moment="start_turn")

    def apply(self, target):
        print(f"{target.nom} est étourdi et saute son tour !")


class Brulure(StatusEffect):
    """4ème statut : Brûlure (dégâts fin de tour)."""
    def __init__(self, damage_per_turn=12, duration=2):
        super().__init__("Brûlure", duration, trigger_moment="end_turn")
        self.damage_per_turn = damage_per_turn

    def apply(self, target):
        target.pv -= self.damage_per_turn
        print(f" {target.nom} brûle et perd {self.damage_per_turn} PV (reste {target.pv})")


# ======================
# Gestion générique des statuts
# ======================

def appliquer_statut(cible, statut):
    """Ajoute un statut à la liste de la cible."""
    cible.statuts.append(statut)
    print(f"{cible.nom} reçoit le statut {statut.nom}.")


def traiter_statuts_debut_tour(entite):
    """Appelé au début du tour d’une entité."""
    nouveaux_statuts = []
    for statut in entite.statuts:
        if statut.trigger_moment == "start_turn":
            statut.apply(entite)
        # tick gère la durée et l’expiration
        if statut.tick(entite):
            nouveaux_statuts.append(statut)
    entite.statuts = nouveaux_statuts


def reduire_degats_par_bouclier(entite, degats):
    """
    Passe les dégâts au travers de tous les boucliers.
    Ne touche pas le moteur de combat : il appelle juste cette fonction.
    """
    nouveaux_statuts = []
    dmg = degats
    for statut in entite.statuts:
        if isinstance(statut, Shield):
            dmg = statut.absorb_damage(entite, dmg)
        # tick pour gérer la durée (tour, nombre de coups, etc.)
        if statut.tick(entite):
            nouveaux_statuts.append(statut)
    entite.statuts = nouveaux_statuts
    return dmg


def est_etourdi(entite):
    """Renvoie True si un statut Etourdissement actif est présent."""
    for statut in entite.statuts:
        if isinstance(statut, Stun):
            return True
    return False


# =====================
# Combat et actions
# =====================

def calcul_degats(attaquant, cible):
    """Dégâts physiques de base avec variance et critique."""
    defense_cible = getattr(cible, "defense", 0)
    base = attaquant.force1 - defense_cible
    variance = random.randint(-2, 2)
    degats = base + variance

    if random.random() < 0.10:
        degats = int(degats * 2)
        print("Coup critique !")

    if degats < 1:
        degats = 1

    # passage dans les boucliers éventuels
    degats = reduire_degats_par_bouclier(cible, degats)

    return degats


def tenter_fuite(personnage, ennemi):
    agilite_ennemi = getattr(ennemi, "agilite", 0)
    chance_fuite = 0.5 + (personnage.agilite - agilite_ennemi) * 0.01
    chance_fuite = max(0.1, min(0.9, chance_fuite))

    if random.random() < chance_fuite:
        print(f"{personnage.nom} réussit à fuir !")
        return True
    else:
        print(f"{personnage.nom} échoue à fuir...")
        return False


def action_attaquer(attaquant, cible):
    if est_etourdi(attaquant):
        print(f"{attaquant.nom} est étourdi et ne peut pas attaquer ce tour.")
        return
    degats = calcul_degats(attaquant, cible)
    cible.pv -= degats
    print(f"{attaquant.nom} attaque {cible.nom} et inflige {degats} dégâts. Il reste {cible.pv} PV à {cible.nom}.")
    if isinstance(cible, Ennemi):
        cible.mettre_a_jour_phase()


def action_defendre(personnage):
    personnage.defense += 5
    print(f"{personnage.nom} se met en défense et augmente sa défense de 5 pour ce tour.")


def action_competence(personnage, competence, cible):
    if est_etourdi(personnage):
        print(f"{personnage.nom} est étourdi et ne peut pas utiliser de compétence.")
        return

    if competence not in personnage.competences:
        print(f"{personnage.nom} ne possède pas la compétence {competence}.")
        return

    print(f"{personnage.nom} utilise {competence} sur {cible.nom}.")

    if competence == "Coup puissant":
        degats = int(calcul_degats(personnage, cible) * 1.5)
        cible.pv -= degats
        print(f"Attaque puissante ! {cible.nom} perd {degats} PV (reste {cible.pv}).")
    elif competence == "Boule de feu":
        defense_cible = getattr(cible, "defense", 0)
        degats = int((personnage.intelligence * 1.2) - defense_cible)
        if degats < 1:
            degats = 1
        cible.pv -= degats
        print(f"Boule de feu ! {cible.nom} perd {degats} PV (reste {cible.pv}).")
        # exemple : applique Poison via une variante
        appliquer_statut(cible, Poison(damage_per_turn=8, duration=3))
    elif competence == "Bouclier":
        appliquer_statut(personnage, Shield(shield_points=40, duration=3))
    elif competence == "Attaque sournoise":
        degats = int(calcul_degats(personnage, cible) * 1.2)
        cible.pv -= degats
        print(f"Attaque sournoise ! {cible.nom} perd {degats} PV (reste {cible.pv}).")
        # chance d’étourdir
        if random.random() < 0.3:
            appliquer_statut(cible, Stun(duration=1))
    else:
        print("Effet de cette compétence non encore implémenté.")


def action_objet(personnage, objet, cible=None):
    if est_etourdi(personnage):
        print(f"{personnage.nom} est étourdi et ne peut pas utiliser d'objet.")
        return

    if objet == "potion":
        soin = 30
        personnage.pv += soin
        print(f"{personnage.nom} utilise une potion et récupère {soin} PV (total {personnage.pv}).")
    elif objet == "bombe" and cible is not None:
        degats = 40
        cible.pv -= degats
        print(f"{personnage.nom} lance une bombe sur {cible.nom}, qui perd {degats} PV (reste {cible.pv}).")
    else:
        print(f"Objet {objet} non géré pour l’instant.")

# =========================
# NOUVELLES COMPÉTENCES AVEC COMBO
# =========================

class Guerrier(Personnage):
    def __init__(self, nom):
        competences = ["Coup puissant", "Charge", "Attaque empoisonnée"]  # Combo ajoutée
        super().__init__(
            nom=nom, type_="Guerrier", pv=100, pv_max=200, intelligence=40, agilite=50,
            competences=competences, force1=50, force2=60, defense=20
        )
# ==========================
# SYSTÈME D'EXPLORATION
# ==========================

class Zone:
    def __init__(self, nom, description, evenements, ennemis_possibles, acces):
        self.nom = nom
        self.description = description
        self.evenements = evenements  # liste pondérée d'événements
        self.ennemis_possibles = ennemis_possibles
        self.acces = acces  # conditions d'accès (clé, etc.)

# =========================
# MOTEUR DE COMBAT INTERACTIF
# =========================

def combat_interactif(personnage, ennemi):
    """Combat avec menu interactif."""
    tour = 1
    while personnage.pv > 0 and ennemi.pv > 0:
        print(f"\n--- Tour {tour} ---")
        print(f"{personnage.nom}: {personnage.pv}/{personnage.pv_max} PV | {ennemi.nom}: {ennemi.pv} PV")
        
        # Statuts
        traiter_statuts_debut_tour(personnage)
        traiter_statuts_debut_tour(ennemi)
        
        if personnage.pv <= 0 or ennemi.pv <= 0: break
        
        # Menu joueur
        print("\n1. Attaquer | 2. Compétence | 3. Objet | 4. Défendre | 5. Fuir")
        choix = input("Action : ").strip()
        
        if choix == "1":
            action_attaquer(personnage, ennemi)
        elif choix == "2":
            print("Compétences:", ", ".join(personnage.competences))
            comp = input("Choisir : ")
            action_competence(personnage, comp, ennemi)
        elif choix == "3":
            if personnage.inventory.has_item("Potion de soin"):
                potion = personnage.inventory.get_item("Potion de soin")
                personnage.inventory.remove_item(potion)
                personnage.pv = min(personnage.pv_max, personnage.pv + 40)
                print(f"+40 PV ({personnage.pv}/{personnage.pv_max})")
        elif choix == "4":
            action_defendre(personnage)
        elif choix == "5":
            if tenter_fuite(personnage, ennemi): break
        
        # Tour ennemi
        if ennemi.pv > 0 and not est_etourdi(ennemi):
            # IA simple améliorée
            if random.random() < 0.3 and "competence_speciale" in ennemi.particularites:
                appliquer_statut(personnage, Brulure())
            else:
                # Ajouter force1 aux ennemis pour qu'ils attaquent
                if not hasattr(ennemi, 'force1'): setattr(ennemi, 'force1', 25)
                action_attaquer(ennemi, personnage)
        
        # Fin tour statuts end_turn
        for statut in personnage.statuts + ennemi.statuts:
            if statut.trigger_moment == "end_turn":
                statut.apply(personnage if isinstance(statut, Brulure) else ennemi)
        
        tour += 1
        # Fin de combat : message clair
        if personnage.pv <= 0:
            print(f"\n{personnage.nom} est vaincu...")
        elif ennemi.pv <= 0:
            print(f"\n{ennemi.nom} est vaincu !")

# ========================
# FONCTION PRINCIPALE
# ========================

def jeu_principal():
    print(" L'AVENTURE DU DONJON PERDU - VERSION ULTIME ")
    print("\n1. Nouvelle partie ")
    print("2. Charger sauvegarde ")
    choix = input("→ ").strip()
    
    if choix == "2":
        jeu = Jeu("normal")  # Difficulté par défaut pour chargement
        joueur = jeu.charger()
        if not joueur:
            print(" Sauvegarde corrompue → Nouvelle partie")
            return nouvelle_partie()
    else:
        nouvelle_partie()
    
    # Boucle principale avec TOUS les menus
    while joueur.pv > 0 and not jeu.quete.est_terminee():
        jeu.explorer(joueur)
        
        print("\n" + "="*60)
        print("MENU COMPLET :")
        print("1. Village     2. Forêt     3. Donjon ")
        print("4. Status     5. Sauvegarder     6. Marchand ")
        print("0. Quitter ")
        choix = input("→ ").strip()
        
        if choix == "1":
            jeu.deplacer("village")
        elif choix == "2":
            jeu.deplacer("foret")
            jeu.nb_explorations_foret += 1
        elif choix == "3":
            jeu.deplacer("donjon")
        elif choix == "4":
            print_status(joueur, jeu)
        elif choix == "5":
            jeu.sauvegarder(joueur)
        elif choix == "6":
            jeu.evenement_marchand(joueur)
        elif choix == "0":
            break
    
    if jeu.quete.est_terminee():
        print("\n LÉGENDE ACCOMPLIE ! Le village est sauvé !")

def nouvelle_partie():
    """Gestion propre de nouvelle partie."""
    global joueur, jeu  # Si besoin global, sinon return
    
    diff = input("Difficulté (f/n/d) [n] : ").lower() or 'n'
    diff_map = {'f': 'facile', 'n': 'normal', 'd': 'difficile'}
    difficulte = diff_map.get(diff, 'normal')
    
    nom = input("Nom du héros : ")
    print("\n1. Guerrier | 2. Mage | 3. Voleur ")
    choix_classe = input("Classe : ").strip()
    classes = {"1": Guerrier, "2": Mage, "3": Voleur}
    Classe = classes.get(choix_classe, Guerrier)
    
    joueur = Classe(nom)
    jeu = Jeu(difficulte)
    
    print(f"\n {joueur.nom} le {joueur.type} prêt pour l'aventure ({difficulte.upper()})!")
    print(f" Objectif : {jeu.quete.description[0]}")
    return joueur, jeu

def print_status(joueur, jeu):
    """Menu status détaillé."""
    print(f"\n {joueur.nom} ({joueur.type})")
    print(f" PV: {joueur.pv}/{joueur.pv_max} | ATK: {joueur.attaque}")
    print(f" DEF: {joueur.defense} | INT: {joueur.intelligence}")
    print(f" Inventaire: {len(joueur.inventory.items)}/10")
    print(f"Zone: {jeu.position.upper()} |  Or: {jeu.or_}")
    print(f" Quête: {jeu.quete.description[jeu.quete.etat]}")


# ==========================
# SYSTÈME DE QUÊTE PRINCIPALE
# ==========================

class QuetePrincipale:
    def __init__(self):
        self.etat = 0  # 0: chercher clé, 1: donjon accessible, 2: terminé
        self.description = [
            " Trouver la Clé du Donjon dans la Forêt",
            " Vaincre le Gardien du Donjon",
            " Quête terminée !"
        ]

    def progresser(self):
        if self.etat < 2:
            self.etat += 1
            print(f" Progression : {self.description[self.etat]}")

    def est_terminee(self):
        return self.etat == 2

    def peut_entrer_donjon(self):
        return self.etat >= 1

class Jeu:
    def __init__(self):
        self.zones = {
            "village": Zone(
                nom="Village",
                description=" Village sûr - Prépare-toi pour l'aventure !",
                evenements=[("dialogue", 0.5), ("marchand", 0.3), ("repos", 0.2)],
                ennemis_possibles=[],
                acces=None
            ),
            "foret": Zone(
                nom="Forêt",
                description=" Forêt dangereuse - Cherche la Clé du Donjon ici !",
                evenements=[("combat", 0.4), ("coffre", 0.3), ("dialogue", 0.2), ("cle", 0.1)],
                ennemis_possibles=[LoupSauvage, Bandit, Squelette],
                acces=None
            ),
            "donjon": Zone(
                nom="Donjon",
                description=" Donjon scellé - Seul le Gardien reste...",
                evenements=[("combat", 0.5), ("coffre", 0.4), ("boss", 0.1)],
                ennemis_possibles=[ChampionCorrompu],
                acces="quete"
            )
        }
        self.position = "village"
        self.quete = QuetePrincipale()
        self.or_ = 50
        self.nb_explorations_foret = 0
        
    def tirer_evenement(self, evenements):
        """Tirage pondéré d'événement."""
        evenements_possibles = []
        poids_total = 0
        for evt, poids in evenements:
            evenements_possibles.extend([evt] * int(poids * 10))
            poids_total += poids
        if not evenements_possibles:
            return "rien"  # Sécurité si liste vide

        return random.choice(evenements_possibles)

    def status_quete(self):
        """Affiche l'état actuel de la quête."""
        print(f"\n QUÊTE PRINCIPALE : {self.quete.description[self.quete.etat]}")
        print(f" Or : {self.or_} | Zone : {self.position.upper()}")
        if self.quete.etat == 0:
            print(" Indice : Explore la Forêt pour trouver la Clé !")

    def explorer(self, joueur):
        zone = self.zones[self.position]

        # Vérifier accès donjon
        if self.position == "donjon" and not self.quete.peut_entrer_donjon():
            print(" Le donjon est scellé ! Trouve d'abord la Clé dans la Forêt.")
            return False

        self.status_quete()
        print(f"\n{'='*50}")
        print(f" {zone.description}")
        print('='*50)

        evenement = self.tirer_evenement(zone.evenements)

        if evenement == "combat":
            return self.evenement_combat(joueur, zone)
        elif evenement == "coffre":
            return self.evenement_coffre(joueur, zone)
        elif evenement == "marchand":
            self.evenement_marchand(joueur)
        elif evenement == "dialogue":
            self.evenement_dialogue()
        elif evenement == "cle":
            self.evenement_cle()
        elif evenement == "boss":
            return self.evenement_boss(joueur)
        elif evenement == "repos":
            self.evenement_repos(joueur)
        
        return True  # Continue l'exploration


    def evenement_dialogue(self):
        dialogues = {
            "village": "L'aubergiste : 'Les legendes parlent d'une cle cachée dans la foret...'", 
            "foret": "Tu trouves une vieille inscription : 'Seul le cœur pur trouve la clé...'",
            "donjon": "Une voix spectrale : 'Prouve ta valeur face au Gardien !'"
        }
        print(dialogues.get(self.position, "Quelque chose d'interessant..."))

    def evenement_marchand(self, joueur):
        print("Un marchand itinerant t'aborde :")
        print("1. Potion de soin (20 or)")
        print("2. Epee d'acier (50 or)") 
        print("3. Armure renforcee (40 or)")
        print("4. Quitter")
        
        choix = input("Choix : ")
        if choix == "1" and self.or_ >= 20:
            self.or_ -= 20
            potion = Consumable("Potion de soin", "soin_30")
            joueur.inventory.add_item(potion)
            print("Potion achetée !")
        elif choix == "2" and self.or_ >= 50:
            self.or_ -= 50
            epee = Weapon("Epee d'acier", attack_bonus=15)
            joueur.inventory.add_item(epee)
            print("Epee d'acier achetée !")
        elif choix == "3" and self.or_ >= 40:
            self.or_ -= 40
            armure = Armor("Armure renforcee", defense_bonus=10)
            joueur.inventory.add_item(armure)
            print("Armure renforcee achetée !")
        else:
            print("Pas assez d'or ou choix invalide.")

    def evenement_repos(self, joueur):
        soin = min(50, joueur.pv_max - joueur.pv)
        joueur.pv += soin
        print(f"Repos au village. +{soin} PV (total: {joueur.pv})")


    def evenement_combat(self, joueur, zone):
        ennemi_classe = random.choice(zone.ennemis_possibles)
        ennemi = ennemi_classe()
        print(f"\n{ennemi.nom} apparaît !")
        input("Appuie sur Entree pour combattre...")
        combat_interactif(joueur, ennemi)  # combat interactif

        if ennemi.pv <= 0:
            gain_or = random.randint(10, 30)
            self.or_ += gain_or
            print(f"+{gain_or} or (Total: {self.or_})")

            if self.quete.etat == 0 and random.random() < 0.4:
                self.quete.progresser()
                print("LA CLÉ DU DONJON tombe du cadavre !")
                print("Combat terminé. Appuie sur Entrée pour continuer...")
                input()
                return True
        return False


    def combat(self, joueur, ennemi):
        if ennemi.pv <= 0:
            gain_or = random.randint(10, 30)
            self.or_ += gain_or
            print(f" +{gain_or} or (Total: {self.or_})")

            # Chance de drop clé (étape 1)
            if self.quete.etat == 0 and random.random() < 0.4:
                self.quete.progresser()
                print(" LA CLÉ DU DONJON tombe du cadavre !")
                return True
        return False

    def evenement_coffre(self, joueur, zone):
        if self.quete.etat == 0 and zone.nom == "Forêt" and random.random() < 0.6:
            # Coffre spécial : CLÉ DU DONJON
            self.quete.progresser()
            print(" COFFRE MYSTÉRIEUX ! Tu trouves la CLÉ DU DONJON !")
            return True

        # Coffre normal
        loots = [
            (Consumable("Potion de soin", "soin"), " Potion de soin"),
            (Weapon("Dague affûtée", 8), " Dague affûtée (+8 ATK)"),
            (Armor("Manteau renforcé", 5), " Manteau renforcé (+5 DEF)"),
            ("or", 25)
        ]
        loot = random.choice(loots)

        if isinstance(loot, tuple) and loot[0] == "or":
            self.or_ += loot[1]
            print(f" +{loot[1]} or trouvé !")
        else:
            item, message = loot
            if joueur.inventory.add_item(item):
                print(message)
        return True

    def evenement_cle(self):
        """Événement dédié à la clé (rare)."""
        self.quete.progresser()
        print(" Un éclat mystérieux apparaît ! C'est la CLÉ DU DONJON !")
        return True

    def evenement_boss(self, joueur):
        print("\n === COMBAT FINAL ===")
        print("Le GARDIEN DU DONJON se dresse devant toi !")
        input("Appuie sur Entrée pour le dernier combat...")

        boss = GardienDonjon()
        combat_interactif(joueur, boss)
        if boss.pv <= 0:
            self.quete.progresser()
            self.donner_recompense_finale(joueur)
            return False  # Fin du jeu
        return True

    def donner_recompense_finale(self, joueur):
        """Récompense légendaire pour la victoire finale."""
        print("\n FÉLICITATIONS ! Tu as sauvé le village !")
        print(" Récompense légendaire :")

        # Arme OU armure légendaire (au hasard)
        if random.random() < 0.5:
            arme = Weapon("Épée du Gardien", attack_bonus=25, int_bonus=10)
            joueur.inventory.add_item(arme)
            joueur.equip_weapon(arme)
            print(" Épée du Gardien équipée automatiquement (+25 ATK, +10 INT)")
        else:
            armure = Armor("Armure Ancestrale", defense_bonus=20, int_bonus=15)
            joueur.inventory.add_item(armure)
            joueur.equip_armor(armure)
            print(" Armure Ancestrale équipée (+20 DEF, +15 INT)")

    def deplacer(self, nouvelle_zone):
        ancien = self.position
        self.position = nouvelle_zone
        print(f"\n{ancien.upper()} → {nouvelle_zone.upper()}")

    def sauvegarder(self, nom_fichier="sauvegarde.json"):
        import json
        data = {
            "position": self.position,
            "quete_etat": self.quete.etat,
            "or": self.or_,
            "nb_explorations_foret": self.nb_explorations_foret
        }
        with open(nom_fichier, 'w') as f:
            json.dump(data, f)
        print(f"Sauvegardé dans {nom_fichier}")

# ==========================
# SERIALISATION PERSONNAGE
# ==========================

@dataclass
class SauvegardePersonnage:
    """Structure plate pour JSON """
    nom: str
    type: str
    pv: int
    pv_max: int
    intelligence: int
    agilite: int
    force1: int
    force2: int
    defense_base: int
    competences: List[str]
    inventaire: List[Dict[str, Any]]
    weapon_equipee: Dict[str, Any] = None
    armor_equipee: Dict[str, Any] = None


class SauvegardeJeu:
    """Structure complète de sauvegarde."""
    def __init__(self):
        self.personnage: SauvegardePersonnage = None
        self.position: str = "village"
        self.quete_etat: int = 0
        self.or_: int = 50
        self.nb_explorations_foret: int = 0

# Ajoute ces méthodes à la classe Personnage (indentation au niveau de def __init__)
def to_dict(self) -> Dict[str, Any]:
    """Convertit le personnage en dict sérialisable."""
    return {
        "nom": self.nom,
        "type": self.type,
        "pv": self.pv,
        "pv_max": 100,  # fixe pour l'instant
        "intelligence": self.intelligence,
        "agilite": self.agilite,
        "force1": self.force1,
        "force2": self.force2,
        "defense_base": self.defense_base,
        "competences": self.competences,
        "weapon_equipee": self.weapon.to_dict() if self.weapon else None,
        "armor_equipee": self.armor.to_dict() if self.armor else None,
        "inventaire": [item.to_dict() for item in self.inventory.items]
    }

def from_dict(self, data: Dict[str, Any]):
    """Restaure le personnage depuis dict."""
    self.nom = data["nom"]
    self.type = data["type"]
    self.pv = data["pv"]
    self.pv_max = data["pv_max"]
    self.intelligence = data["intelligence"]
    self.agilite = data["agilite"]
    self.force1 = data["force1"]
    self.force2 = data["force2"]
    self.defense_base = data["defense_base"]
    self.competences = data["competences"]
    self.inventory = Inventory(capacity=10)
    
    # Restaurer inventaire
    for item_data in data["inventaire"]:
        item = self.creer_item_from_dict(item_data)
        self.inventory.add_item(item)
    
    # Équipements
    if data["weapon_equipee"]:
        self.weapon = self.creer_item_from_dict(data["weapon_equipee"])
    if data["armor_equipee"]:
        self.armor = self.creer_item_from_dict(data["armor_equipee"])

def creer_item_from_dict(data: Dict[str, Any]) -> Item:
    """Fabrique un Item depuis ses données sérialisées."""
    item_type = data.get("item_type", "Item")
    
    if item_type == "Weapon":
        return Weapon(data["name"], data["attack_bonus"], data.get("int_bonus", 0))
    elif item_type == "Armor":
        return Armor(data["name"], data["defense_bonus"], data.get("int_bonus", 0))
    elif item_type == "Consumable":
        return Consumable(data["name"], data["effect"])
    else:
        return Item(data["name"])

# Ajoute ces méthodes aux classes Item, Weapon, Armor, Consumable
def to_dict(self) -> Dict[str, Any]:  # Pour Item
    return {"name": self.name, "item_type": self.__class__.__name__}

def to_dict(self) -> Dict[str, Any]:  # Pour Weapon (override)
    return {
        "name": self.name,
        "item_type": "Weapon",
        "attack_bonus": self.attack_bonus,
        "int_bonus": getattr(self, "int_bonus", 0)
    }

def to_dict(self) -> Dict[str, Any]:  # Pour Armor
    return {
        "name": self.name,
        "item_type": "Armor",
        "defense_bonus": self.defense_bonus,
        "int_bonus": getattr(self, "int_bonus", 0)
    }

def to_dict(self) -> Dict[str, Any]:  # Pour Consumable
    return {
        "name": self.name,
        "item_type": "Consumable",
        "effect": self.effect
    }

# ==========================
# MÉTHODES JEU SAUVEGARDE
# ==========================

# Remplace la méthode sauvegarder existante dans Jeu
def sauvegarder(self, joueur, nom_fichier="sauvegarde.json"):
    """Sauvegarde complète du jeu."""
    sauvegarde = SauvegardeJeu()
    sauvegarde.personnage = SauvegardePersonnage(**joueur.to_dict())  # joueur passé en paramètre
    sauvegarde.position = self.position
    sauvegarde.quete_etat = self.quete.etat
    sauvegarde.or_ = self.or_
    sauvegarde.nb_explorations_foret = self.nb_explorations_foret
    
    with open(nom_fichier, 'w', encoding='utf-8') as f:
        json.dump(asdict(sauvegarde), f, indent=2, ensure_ascii=False)
    
    print(f" Sauvegarde créée : {nom_fichier}")
    print(" PV:", sauvegarde.personnage.pv, f"/{sauvegarde.personnage.pv_max}")

def charger(self, nom_fichier="sauvegarde.json"):
    """Restaure complètement l'état du jeu."""
    if not os.path.exists(nom_fichier):
        print(" Aucune sauvegarde trouvée.")
        return None
    
    with open(nom_fichier, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Restaurer jeu
    self.position = data["position"]
    self.quete.etat = data["quete_etat"]
    self.or_ = data["or_"]
    self.nb_explorations_foret = data["nb_explorations_foret"]
    
    # Restaurer personnage
    perso_data = data["personnage"]
    nom = perso_data["nom"]
    
    # Recréer le bon type de personnage
    if perso_data["type"] == "Guerrier":
        joueur = Guerrier(nom)
    elif perso_data["type"] == "Mage":
        joueur = Mage(nom)
    elif perso_data["type"] == "Voleur":
        joueur = Voleur(nom)
    else:
        joueur = Guerrier(nom)
    
    # Appliquer les données sauvegardées
    joueur.from_dict(perso_data)
    
    print(f" Chargé : {joueur.nom} ({joueur.type})")
    print(f" Zone : {self.position} |  Or : {self.or_}")
    print(f" Quête : {self.quete.description[self.quete.etat]}")
    
    return joueur

# ==========================
# JEU PRINCIPAL FINAL
# ==========================

def jeu_principal():
    print(" L'Aventure du Donjon Perdu ")
    
    # Menu initial
    print("\n1. Nouvelle partie ")
    print("2. Charger sauvegarde ")
    choix = input("Choix : ").strip()
    
    if choix == "2":
        jeu = Jeu()
        joueur = jeu.charger()
        if not joueur:
            print("Nouvelle partie par défaut.")
            nom = input("Nom : ")
            joueur = Guerrier(nom)
    else:
        # Nouvelle partie
        nom = input("Nom du héros : ")
        print("\n1. Guerrier | 2. Mage | 3. Voleur")
        classe_choix = input("Classe : ")
        classes = {"1": Guerrier(nom), "2": Mage(nom), "3": Voleur(nom)}
        joueur = classes.get(classe_choix, Guerrier(nom))
        jeu = Jeu()
    
    # Boucle principale
    while joueur.pv > 0 and not jeu.quete.est_terminee():
        if not jeu.explorer(joueur):
            break
        
        print("\n" + "═" * 60)
        print(" MENU PRINCIPAL :")
        print("1. Village   2. Forêt   3. Donjon ")
        print("4. Status  5. Sauvegarder   6. Charger   0. Quitter ")
        choix = input("→ ").strip()
        
        if choix == "1": jeu.deplacer("village")
        elif choix == "2": 
            jeu.deplacer("foret")
            jeu.nb_explorations_foret += 1
        elif choix == "3": jeu.deplacer("donjon")
        elif choix == "4":
            print(f"{joueur.nom} | PV: {joueur.pv}/{100}")
            print(f" ATK: {joueur.attaque} |  DEF: {joueur.defense}")
            print(f" {len(joueur.inventory.items)}/{joueur.inventory.capacity} objets")
        elif choix == "5":
            jeu.sauvegarder(joueur)
        elif choix == "6":
            joueur_temp = jeu.charger()
            if joueur_temp: joueur = joueur_temp
        elif choix == "0": break
    
    if jeu.quete.est_terminee():
        print("\n LÉGENDE ACCOMPLIE ! Le village est sauvé ! ")

# Lancer le jeu
if __name__ == "__main__":
    jeu_principal()