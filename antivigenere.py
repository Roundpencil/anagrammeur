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

def charger_dictionnaire(chemin_fichier: str, taille: int):
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
        mots_uniques = set(standardiser_chaine(mot.strip().lower()) for mot in f if len(mot.strip())==taille)

    return list(mots_uniques)

if __name__ == "__main__":
    mot_chiffre = "ssklapyl"
    taille = len(mot_chiffre)
    # dictionnaire = ["ATTACKATDAWN", "BONJOURMONDE", "HELLOWORLD"]
    fichier_dico = "liste.de.mots.francais.frgut.txt"
    dictionnaire = charger_dictionnaire(fichier_dico, taille)

    cles = trouver_cles_possibles(mot_chiffre, dictionnaire)
    i = 1
    for clef in cles:
        print(f"{i} : {clef}")
        i += 1