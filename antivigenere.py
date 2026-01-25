import re
from typing import Iterable, List

import unicodedata

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
A2I = {c: i for i, c in enumerate(ALPHABET)}
I2A = {i: c for i, c in enumerate(ALPHABET)}


def cle_vigenere(clair: str, chiffre: str) -> str:
    """Retrouve la clé Vigenère à partir d'un mot clair et du mot chiffré"""
    return "".join(
        I2A[(A2I[ch] - A2I[cl]) % 26]
        for cl, ch in zip(clair, chiffre)
    )


def trouver_cles_possibles(
    mot_chiffre: str,
    dictionnaire: Iterable[str]
) -> List[str]:
    """Retourne toutes les clés Vigenère possibles basées sur un dictionnaire"""
    mot_chiffre = mot_chiffre.upper()

    cles = []
    for mot in dictionnaire:
        mot = mot.upper()
        if len(mot) != len(mot_chiffre):
            continue

        try:
            cle = cle_vigenere(mot, mot_chiffre)
            cles.append(cle)
        except KeyError:
            # Ignore les mots contenant des caractères hors alphabet
            pass

    return cles

def standardiser_chaine(s: str) -> str:
    s = s.lower()
    s = s.replace('œ', 'oe').replace('æ', 'ae')
    s = unicodedata.normalize('NFD', s)
    return re.sub(r'[\u0300-\u036f]', '', s)

def charger_dictionnaire(chemin_fichier: str, taille: int=0):
    """
    Charge le dictionnaire, le pré-filtre et le pré-calcule pour l'optimisation.

    Retourne une liste de tuples (mot, compteur_de_lettres_du_mot),
    triée par longueur de mot décroissante.
    """
    mots_filtres = []

    with open(chemin_fichier, 'r', encoding='utf-8') as f:
        # Utilise un set pour une déduplication initiale rapide
        # mots_uniques = set(mot.strip().lower() for mot in f if mot.strip())
        # mots_uniques = set(standardiser_chaine(mot.strip().lower()) for mot in f if mot.strip())
        if taille:
            mots_uniques = set(standardiser_chaine(mot.strip().lower()) for mot in f if len(mot.strip())==taille)
        else:
            mots_uniques = set(standardiser_chaine(mot.strip().lower()) for mot in f)

    return list(mots_uniques)

def identifier_sous_chaines(chaine_dentree:str, dictionnaire: Iterable[str],
                            output:list[tuple[list[str], list[str]]],
                            sortie_en_cours_exacte_complete: tuple[list[str], list[str]] = None,
                            verbal = True):
    if not sortie_en_cours_exacte_complete:
        sortie_en_cours_exacte_complete = ([], [])

    chaine_dentree = chaine_dentree.lower()
    if verbal :
        print(f"entrée = {chaine_dentree}, sortie en cours = {sortie_en_cours_exacte_complete}")

    for mot_dico in dictionnaire:
        if len(chaine_dentree) >= len(mot_dico):
            if chaine_dentree.startswith(mot_dico):
                # si la chaine commence par le mot, on l'ajoute aux solutions possibles
                if verbal:
                    print(f"la chaine {chaine_dentree} commence par {mot_dico}")
                nouvelle_sortie_en_cours = (sortie_en_cours_exacte_complete[0].copy(),
                                            sortie_en_cours_exacte_complete[1].copy())
                nouvelle_sortie_en_cours[0].append(mot_dico)
                nouvelle_sortie_en_cours[1].append(mot_dico)
                # puis on recurse s'il reste des lettres car on a réussi cette étape
                if delta_taille := (len(chaine_dentree) - len(mot_dico)):
                    if verbal:
                        print(f"deltataille = {delta_taille} > on récuse")
                    nouvelle_chaine_entree = chaine_dentree[len(chaine_dentree)-delta_taille:]
                    return identifier_sous_chaines(nouvelle_chaine_entree, dictionnaire,
                                                   output, nouvelle_sortie_en_cours)
                else:
                    if verbal:
                        print(f"deltataille = {delta_taille} > on arrête là")
                    # sinon, s'il n'y a plus de lettres, on a fini la récursion complète
                    # on ajoute la solution aux solutions valides
                    code_retour = 0 # le code qui dit qu'on a une solution
                    output.append(nouvelle_sortie_en_cours)
                    # puis on laisse la boucle sur le dictionnaire se poursuivre
                    print(f"\tsolution ajoutée = {sortie_en_cours_exacte_complete}")

            # sinon : on ne fait rien, la boucle meurt d'elle meme
        else:
            # dans ce cas, on a une entrée plus lonque que le mot
            # on va donc chercher dans les premières lettres du mot
            if mot_dico.startswith(chaine_dentree):
                # si le mot_dico  commence par les lettres qu'il reste, on l'ajoute aux solutions possibles
                if verbal:
                    print(f"le mot_dico {mot_dico} commence par les lettres qu'il reste({chaine_dentree}), "
                      f"on l'ajoute aux solutions possibles")
                nouvelle_sortie_en_cours = (sortie_en_cours_exacte_complete[0].copy(),
                                            sortie_en_cours_exacte_complete[1].copy())
                nouvelle_sortie_en_cours[0].append(mot_dico[0:len(chaine_dentree)])
                nouvelle_sortie_en_cours[1].append(mot_dico)
                output.append(nouvelle_sortie_en_cours)
                if verbal:
                    print(f"on arrête là")
                print(f"\tsolution ajoutée = {sortie_en_cours_exacte_complete}")






    pass

if __name__ == "__main__":
    mot_chiffre = "ssklapyl"
    ma_taille = len(mot_chiffre)
    # dictionnaire = ["ATTACKATDAWN", "BONJOURMONDE", "HELLOWORLD"]
    fichier_dico = "liste.de.mots.francais.frgut.txt"
    dictionnaire = charger_dictionnaire(fichier_dico, ma_taille)

    cles = trouver_cles_possibles(mot_chiffre, dictionnaire)
    cles = cles[:100]
    # i = 1
    # for clef in cles:
    #     print(f"{i} : {clef}")
    #     i += 1

    #puis on croise les clefs avec les mots qu'on connait

    dictionnaire = charger_dictionnaire(fichier_dico)
    sortie_globale = []

    for mot in cles:
        sortie = []
        identifier_sous_chaines(mot, dictionnaire, sortie)
        if sortie:
            sortie_globale.append(sortie)

    print(sortie_globale)
    i = 1
    for s in sortie_globale:
        print(f"{i} : {s}")
        i += 1

