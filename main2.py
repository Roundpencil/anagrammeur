import re
import sys
import argparse
from collections import Counter
from typing import List, Dict, Tuple, Optional

import unicodedata

# Cache pour la mémoïsation. La clé ne doit contenir QUE l'état du problème
# (lettres, jokers), et non des paramètres de la recherche (comme la profondeur).
# C'est un point critique pour la performance.
memo: Dict[Tuple[frozenset, int], List[List[str]]] = {}


def standardiser_chaine(s: str) -> str:
    s = s.lower()
    s = s.replace('œ', 'oe').replace('æ', 'ae')
    s = unicodedata.normalize('NFD', s)
    return re.sub(r'[\u0300-\u036f]', '', s)

def charger_dictionnaire(chemin_fichier: str, lettres_disponibles: Counter, jokers: int) -> List[Tuple[str, Counter]]:
    """
    Charge, pré-filtre et pré-calcule le dictionnaire pour une optimisation maximale.
    Retourne une liste de tuples (mot, compteur_de_lettres), triée par longueur décroissante.
    """
    longueur_max = sum(lettres_disponibles.values()) + jokers
    mots_filtres = []

    try:
        with open(chemin_fichier, 'r', encoding='utf-8') as f:
            # mots_uniques = set(mot.strip().lower() for mot in f if mot.strip())
            mots_uniques = set(standardiser_chaine(mot.strip().lower()) for mot in f if mot.strip())
    except FileNotFoundError:
        print(f"Erreur: Le fichier dictionnaire '{chemin_fichier}' est introuvable.", file=sys.stderr)
        # Création d'un fichier d'exemple pour la première utilisation
        try:
            with open("dictionnaire.txt", "w", encoding='utf-8') as f_ex:
                f_ex.write("bouton\nboulon\nou\nbout\nbon\nton\nloup\n")
            print("Info: Un fichier 'dictionnaire.txt' d'exemple a été créé. Veuillez relancer la commande.",
                  file=sys.stderr)
        except IOError as e:
            print(f"Erreur: Impossible de créer le fichier dictionnaire d'exemple: {e}", file=sys.stderr)
        sys.exit(1)

    for mot in mots_uniques:
        if len(mot) > longueur_max:
            continue

        compteur_mot = Counter(mot)
        jokers_necessaires = sum((compteur_mot - lettres_disponibles).values())

        if jokers_necessaires <= jokers:
            mots_filtres.append((mot, compteur_mot))

    mots_filtres.sort(key=lambda x: len(x[0]), reverse=True)
    return mots_filtres


def trouver_anagrammes_recursif(
        lettres_restantes: Counter,
        jokers_restants: int,
        dictionnaire_prefiltre: List[Tuple[str, Counter]],
        max_mots: Optional[int],
        lettres_ignorees: int,
        profondeur_actuelle: int
) -> List[List[str]]:
    """
    Fonction récursive avec mémoïsation pour trouver toutes les chaînes d'anagrammes.
    """
    # 1. Condition d'arrêt pour la profondeur maximale (élagage/pruning)
    # Si on a déjà atteint le nombre max de mots, on arrête d'explorer cette branche.
    if max_mots is not None and profondeur_actuelle >= max_mots:
        return []

    # 2. Cas de base : si le nombre de ressources restantes est dans la tolérance,
    # c'est une solution valide (un chemin vide à partir d'ici).
    solutions_locales = []
    if sum(lettres_restantes.values()) + jokers_restants <= lettres_ignorees:
        solutions_locales.append([])

    # 3. Mémoïsation : vérifier si cet état exact (lettres, jokers) a déjà été résolu
    etat_actuel = (frozenset(lettres_restantes.items()), jokers_restants)
    if etat_actuel in memo:
        # On filtre les résultats du cache pour respecter la contrainte de `max_mots`
        # pour les chemins futurs.
        cached_results = memo[etat_actuel]
        if max_mots is None:
            return solutions_locales + cached_results
        else:
            filtered_results = [res for res in cached_results if profondeur_actuelle + len(res) < max_mots]
            return solutions_locales + filtered_results

    solutions_trouvees = []
    longueur_restante = sum(lettres_restantes.values()) + jokers_restants

    for mot, compteur_mot in dictionnaire_prefiltre:
        if len(mot) > longueur_restante:
            continue

        jokers_necessaires = sum((compteur_mot - lettres_restantes).values())

        if jokers_necessaires <= jokers_restants:
            # Le mot est formable, calculons l'état suivant
            nouvelles_lettres = lettres_restantes - compteur_mot
            nouveaux_jokers = jokers_restants - jokers_necessaires

            solutions_enfant = trouver_anagrammes_recursif(
                nouvelles_lettres,
                nouveaux_jokers,
                dictionnaire_prefiltre,
                max_mots,
                lettres_ignorees,
                profondeur_actuelle + 1
            )

            for solution in solutions_enfant:
                solutions_trouvees.append([mot] + solution)

    # Mettre en cache le résultat pour cet état avant de le retourner
    memo[etat_actuel] = solutions_trouvees
    return solutions_locales + solutions_trouvees


def resoudre_anagrammes(
        chaine_entree: str,
        chemin_dictionnaire: str,
        max_mots: Optional[int],
        lettres_ignorees: int
) -> List[str]:
    """
    Fonction principale pour orchestrer la recherche d'anagrammes.
    """
    global memo
    memo.clear()  # Vider le cache pour une nouvelle recherche

    chaine_entree = chaine_entree.lower().strip()
    jokers = chaine_entree.count('?')
    lettres_initiales = Counter(c for c in chaine_entree if c != '?')

    dictionnaire_prefiltre = charger_dictionnaire(chemin_dictionnaire, lettres_initiales, jokers)

    solutions_brutes = trouver_anagrammes_recursif(
        lettres_initiales,
        jokers,
        dictionnaire_prefiltre,
        max_mots,
        lettres_ignorees,
        profondeur_actuelle=0
    )

    # Formater, filtrer et dédoublonner les résultats
    solutions_finales = set()
    for solution in solutions_brutes:
        # Le filtre sur max_mots est déjà géré par l'élagage, mais une double vérification est sûre.
        if solution and (max_mots is None or len(solution) <= max_mots):
            solutions_finales.add(" ".join(sorted(solution)))

    return sorted(list(solutions_finales))


if __name__ == "__main__":
    fichier_dico = "liste.de.mots.francais.frgut.txt"
    chaine_test = "DUSOMEDAEX"
    chaine_test = "TSNNRNOEIMVECUI"
    resultat = resoudre_anagrammes(chaine_test, fichier_dico, 3, 0)
    i = 1
    for r in resultat:
        print(f"{i} : {r}")
        i = i+1

def main():
    parser = argparse.ArgumentParser(
        description="Trouve des anagrammes avec des jokers et des contraintes optionnelles.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument('chaine', help="Chaîne d'entrée avec jokers éventuels (?)")
    parser.add_argument('dictionnaire', help="Chemin vers le fichier dictionnaire")
    parser.add_argument(
        '--max-mots',
        type=int,
        help="Nombre maximum de mots dans une solution. Ex: --max-mots 2"
    )
    parser.add_argument(
        '--lettres-ignorees',
        type=int,
        default=0,
        help="Nombre de caractères (lettres ou jokers) pouvant rester inutilisés. Ex: --lettres-ignorees 1"
    )

    args = parser.parse_args()

    # Validation des arguments
    if args.max_mots is not None and args.max_mots <= 0:
        print("Erreur: --max-mots doit être un nombre positif.", file=sys.stderr)
        sys.exit(1)
    if args.lettres_ignorees < 0:
        print("Erreur: --lettres-ignorees ne peut pas être négatif.", file=sys.stderr)
        sys.exit(1)

    print(f"\n▶ Recherche d'anagrammes pour : '{args.chaine}'")
    print(f"  Dictionnaire : '{args.dictionnaire}'")
    if args.max_mots is not None:
        print(f"  Contrainte : {args.max_mots} mot(s) maximum par solution")
    if args.lettres_ignorees > 0:
        print(f"  Tolérance : jusqu'à {args.lettres_ignorees} caractère(s) ignoré(s)")
    print("-" * 40)

    resultats = resoudre_anagrammes(
        args.chaine,
        args.dictionnaire,
        args.max_mots,
        args.lettres_ignorees
    )

    if not resultats:
        print("Aucune chaîne d'anagramme valide trouvée.")
    else:
        print(f"{len(resultats)} solution(s) unique(s) trouvée(s) :")
        for i, solution in enumerate(resultats, 1):
            print(f"  {i}. {solution}")