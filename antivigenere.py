from typing import Iterable, List

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

def antivigenere():
    mot_chiffre = "LXFOPVEFRNHR"
    dictionnaire = ["ATTACKATDAWN", "BONJOURMONDE", "HELLOWORLD"]

    cles = trouver_cles_possibles(mot_chiffre, dictionnaire)
    print(cles)