import re
import sys
from collections import Counter
from typing import List, Set, Dict, Tuple, Optional

import unicodedata

# Un cache pour la mémoïsation afin de stocker les résultats des sous-problèmes.
# Clé : (frozenset des lettres restantes, nombre de jokers restants)
# Valeur : Liste des chaînes de mots possibles pour cet état.
memo: Dict[Tuple[frozenset, int], List[List[str]]] = {}

def standardiser_chaine(s: str) -> str:
    s = s.lower()
    s = s.replace('œ', 'oe').replace('æ', 'ae')
    s = unicodedata.normalize('NFD', s)
    return re.sub(r'[\u0300-\u036f]', '', s)

def charger_dictionnaire(chemin_fichier: str, lettres_disponibles: Counter, jokers: int) -> List[Tuple[str, Counter]]:
    """
    Charge le dictionnaire, le pré-filtre et le pré-calcule pour l'optimisation.

    Retourne une liste de tuples (mot, compteur_de_lettres_du_mot),
    triée par longueur de mot décroissante.
    """
    longueur_max = sum(lettres_disponibles.values()) + jokers
    mots_filtres = []

    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        # Utilise un set pour une déduplication initiale rapide
        # mots_uniques = set(mot.strip().lower() for mot in f if mot.strip())
        mots_uniques = set(standardiser_chaine(mot.strip().lower()) for mot in f if mot.strip())

    for mot in mots_uniques:
        # 1. Ignorer les mots trop longs
        if len(mot) > longueur_max:
            continue

        compteur_mot = Counter(mot)
        jokers_necessaires = 0
        possible = True

        # 2. Vérifier si le mot est formable avec les lettres et jokers disponibles
        for lettre, quantite in compteur_mot.items():
            if quantite > lettres_disponibles[lettre]:
                jokers_necessaires += quantite - lettres_disponibles[lettre]

            if jokers_necessaires > jokers:
                possible = False
                break

        if possible:
            mots_filtres.append((mot, compteur_mot))

    # 3. Trier par longueur (heuristique : les mots plus longs réduisent plus vite l'espace de recherche)
    mots_filtres.sort(key=lambda x: len(x[0]), reverse=True)
    return mots_filtres


def trouver_anagrammes_recursif(
        lettres_restantes: Counter,
        jokers_restants: int,
        dictionnaire_prefiltre: List[Tuple[str, Counter]]
) -> List[List[str]]:
    """
    Fonction récursive avec mémoïsation pour trouver toutes les chaînes d'anagrammes.
    """
    # Cas de base : si plus de lettres ni de jokers, on a une solution complète (chaîne vide)
    if not any(lettres_restantes.values()) and jokers_restants == 0:
        return [[]]  # Une solution trouvée, qui est une liste vide à laquelle on ajoutera les mots

    # Vérifier si ce sous-problème a déjà été résolu
    etat_actuel = (frozenset(lettres_restantes.items()), jokers_restants)
    if etat_actuel in memo:
        return memo[etat_actuel]

    solutions_trouvees = []
    longueur_restante = sum(lettres_restantes.values()) + jokers_restants

    for mot, compteur_mot in dictionnaire_prefiltre:
        # Optimisation : ignorer les mots plus longs que les lettres restantes
        if len(mot) > longueur_restante:
            continue

        jokers_necessaires = 0
        possible = True

        # Vérifier si le mot est formable avec les ressources actuelles
        for lettre, quantite in compteur_mot.items():
            if quantite > lettres_restantes[lettre]:
                jokers_necessaires += quantite - lettres_restantes[lettre]
            if jokers_necessaires > jokers_restants:
                possible = False
                break

        if possible:
            # Le mot est formable, calculons l'état suivant
            nouvelles_lettres = lettres_restantes - compteur_mot
            # S'assurer que les comptes ne deviennent pas négatifs (gérés par le Counter)
            nouvelles_lettres = Counter({k: v for k, v in nouvelles_lettres.items() if v > 0})
            nouveaux_jokers = jokers_restants - jokers_necessaires

            # Appel récursif pour le reste des lettres
            solutions_enfant = trouver_anagrammes_recursif(nouvelles_lettres, nouveaux_jokers, dictionnaire_prefiltre)

            # Construire les solutions complètes
            for solution in solutions_enfant:
                solutions_trouvees.append([mot] + solution)

    # Mettre en cache le résultat pour cet état avant de le retourner
    memo[etat_actuel] = solutions_trouvees
    return solutions_trouvees


def resoudre_anagrammes(chaine_entree: str, chemin_dictionnaire: str) -> List[str]:
    """
    Fonction principale pour trouver toutes les chaînes d'anagrammes.
    """
    # Nettoyage et comptage initial
    chaine_entree = chaine_entree.lower().strip()
    jokers = chaine_entree.count('?')
    lettres_initiales = Counter(c for c in chaine_entree if c != '?')

    # Charger et filtrer agressivement le dictionnaire
    dictionnaire_prefiltre = charger_dictionnaire(chemin_dictionnaire, lettres_initiales, jokers)

    # Lancer la recherche récursive
    solutions_brutes = trouver_anagrammes_recursif(lettres_initiales, jokers, dictionnaire_prefiltre)

    # Formater et dédoublonner les résultats
    # Le tri garantit que ["ou", "bout"] et ["bout", "ou"] sont traités comme une seule solution
    solutions_finales = set()
    for solution in solutions_brutes:
        solutions_finales.add(" ".join(sorted(solution)))

    return sorted(list(solutions_finales))


# --- Point d'entrée du script ---
if __name__ == "__main__":
    fichier_dico = "liste.de.mots.francais.frgut.txt"
    chaine_test = "DUSOMEDAEX"
    resultats = resoudre_anagrammes(chaine_test, fichier_dico)
    i = 1
    taille_max = 3
    for resultat in resultats:
        if len(resultat.split()) <= taille_max:
            print(f"{i} : {resultat}")
            i +=1

def main():
    # Vérification des arguments de la ligne de commande
    if len(sys.argv) != 3:
        print("Usage: python script.py \"<chaine_avec_jokers>\" <chemin_vers_dictionnaire.txt>")
        # Création d'un fichier dictionnaire pour l'exemple
        try:
            with open("dictionnaire.txt", "w", encoding='utf-8') as f:
                f.write("bouton\n")
                f.write("boulon\n")
                f.write("ou\n")
                f.write("bout\n")
                f.write("test\n")
            print("Info: Un fichier 'dictionnaire.txt' d'exemple a été créé.")
        except IOError as e:
            print(f"Erreur: Impossible de créer le fichier dictionnaire d'exemple: {e}")
        sys.exit(1)

    chaine_test = sys.argv[1]
    fichier_dico = sys.argv[2]

    print(f"\nRecherche d'anagrammes pour : '{chaine_test}'")
    print(f"Utilisation du dictionnaire : '{fichier_dico}'\n")

    try:
        resultats = resoudre_anagrammes(chaine_test, fichier_dico)

        if not resultats:
            print("Aucune chaîne d'anagramme valide trouvée.")
        else:
            print(f"{len(resultats)} solution(s) unique(s) trouvée(s) :")
            for i, solution in enumerate(resultats, 1):
                print(f"  {i}. {solution}")
    except FileNotFoundError:
        print(f"Erreur: Le fichier dictionnaire '{fichier_dico}' n'a pas été trouvé.")
    except Exception as e:
        print(f"Une erreur inattendue est survenue: {e}")