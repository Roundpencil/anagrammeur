import requests
from bs4 import BeautifulSoup
import os
import csv
import sqlite3

def telecharger_fichiers_adresse():
    # URL de la page avec les fichiers
    BASE_URL = "https://adresse.data.gouv.fr/data/ban/adresses/latest/csv-with-ids"

    # Dossier local où sauvegarder les fichiers
    DOWNLOAD_DIR = "ban_csv"

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    # Télécharge la page HTML
    resp = requests.get(BASE_URL)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Trouve tous les liens .csv.gz dans la page
    links = soup.find_all("a", href=True)
    csv_urls = [
        link["href"] for link in links
        if link["href"].endswith(".csv.gz")
    ]

    print(f"Trouvé {len(csv_urls)} fichiers .csv.gz")

    # Téléchargement de chaque fichier
    for url in csv_urls:
        # Si l'URL est relative, la rendre absolue
        if url.startswith("/"):
            url = "https://adresse.data.gouv.fr" + url

        filename = os.path.join(DOWNLOAD_DIR, url.split("/")[-1])
        print(f"Téléchargement {filename}…")

        r = requests.get(url, stream=True)
        r.raise_for_status()

        with open(filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"→ OK")

    print("Téléchargement terminé.")

def creer_bdd(unelignepourtester: bool = False):
    # ====== PARAMÈTRES ======
    DOSSIER_CSV = "ban_csv"
    DB_PATH = "donnees.db"
    TABLE_NAME = "communes"

    # ====== CONNEXION À LA BASE ======
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ====== CRÉATION DE LA TABLE ======
    cursor.execute(f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        libelle_acheminement TEXT,
       nom_afnor TEXT,
       code_postal TEXT,
       UNIQUE(libelle_acheminement, nom_afnor, code_postal)
    )
    """)

    # ====== LECTURE DES CSV ======
    for fichier in os.listdir(DOSSIER_CSV):
        print(f"fichier en cours : {fichier}")
        if fichier.lower().endswith(".csv"):
            chemin_fichier = os.path.join(DOSSIER_CSV, fichier)

            with open(chemin_fichier, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile, delimiter=";")
                print(reader)

                lignes = [
                    (row["libelle_acheminement"], row["nom_afnor"], row["code_postal"])
                    for row in reader
                    if "libelle_acheminement" in row and "nom_afnor" in row and "code_postal" in row
                ]
                print(f"lignes trouvée : {len(lignes)}")

                cursor.executemany(
                    f"""
                    INSERT OR IGNORE INTO {TABLE_NAME} (libelle_acheminement, nom_afnor, code_postal)
                    VALUES (?, ?, ?)
                    """,
                    lignes
                )
        if unelignepourtester:
            break

    # ====== VALIDATION ======
    conn.commit()
    conn.close()

    print("Import terminé ✅")

def afficher_100_premieres_lignes(db_path: str="donnees.db", table: str = "communes"):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute(f"""
    SELECT libelle_acheminement, nom_afnor, code_postal
    FROM {table}
    ORDER BY id
    LIMIT 100
    """)

    lignes = cursor.fetchall()

    conn.close()

    for i, (libelle, afnor, code_postal) in enumerate(lignes, start=1):
        print(f"{i:3d} | {libelle} | {afnor} | {code_postal}")

if __name__ == "__main__":
    creer_bdd()
    # afficher_100_premieres_lignes()