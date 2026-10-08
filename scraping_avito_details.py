import re
import time
import random
import logging
import csv
from pathlib import Path

from bs4 import BeautifulSoup
import pandas as pd

try:
    import undetected_chromedriver as uc
    from selenium.webdriver.common.by import By
    from selenium.common.exceptions import (
        WebDriverException, TimeoutException, NoSuchElementException,
        ElementClickInterceptedException,
    )
except ImportError as e:
    raise SystemExit(
        "Modules manquants. Installez-les avec :\n"
        "  pip install undetected-chromedriver selenium\n"
        f"Erreur d'origine : {e}"
    )

# --------------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------------

BASE_URL_RECHERCHE = "https://www.avito.ma/fr/maroc/voitures_d_occasion-%C3%A0_vendre"
NB_PAGES_RECHERCHE_MAX = 250     # pages de résultats à parcourir pour collecter les liens
OBJECTIF_MIN_ANNONCES = 5000     # nb minimum d'URLs à collecter avant de passer à l'étape 2
DELAI_MIN = 2.5
DELAI_MAX = 5.0
FICHIER_URLS = "urls_annonces.csv"           # sauvegarde intermédiaire (étape 1)
FICHIER_SORTIE = "avito_car_dataset.csv"     # dataset final (étape 2)

# Mettre à True pour AFFICHER le navigateur (utile pour diagnostiquer un
# blocage : on voit alors exactement ce que charge le site en vrai - page
# normale, CAPTCHA visuel, page vide, etc.). Repasser à False une fois le
# problème identifié (le mode headless est plus rapide pour le scraping réel).
MODE_VISIBLE = True

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------
# CHAMPS ATTENDUS (mêmes noms que avito_car_dataset_ALL.csv)
# --------------------------------------------------------------------

# Caractéristiques "1 valeur" : le libellé (alt de l'icône) est identique
# à celui utilisé par Avito dans le HTML -> on s'en sert directement comme
# clé de recherche, ce qui rend le code robuste aux changements de mise en
# page (les classes CSS changent souvent, les libellés d'icônes beaucoup
# moins).
CHAMPS_SPEC = [
    "Année-Modèle", "Kilométrage", "Type de carburant", "Puissance fiscale",
    "Boite de vitesses", "Nombre de portes", "Origine", "Première main",
    "État", "Marque", "Modèle", "Ville", "Secteur",
]

# Équipements : présence/absence d'une icône -> True/False
CHAMPS_EQUIPEMENTS = [
    "Jantes aluminium", "Airbags", "Climatisation",
    "Système de navigation/GPS", "Toit ouvrant", "Sièges cuir",
    "Radar de recul", "Caméra de recul", "Vitres électriques", "ABS", "ESP",
    "Régulateur de vitesse", "Limiteur de vitesse", "CD/MP3/Bluetooth",
    "Ordinateur de bord", "Verrouillage centralisé à distance",
]

COLONNES_FINALES = (
    ["Lien", "Ville", "Secteur", "Marque", "Modèle", "Année-Modèle",
     "Kilométrage", "Type de carburant", "Puissance fiscale",
     "Boite de vitesses", "Nombre de portes", "Origine", "Première main",
     "État"]
    + CHAMPS_EQUIPEMENTS
    + ["Prix"]
)


# --------------------------------------------------------------------
# NAVIGATEUR
# --------------------------------------------------------------------

def creer_navigateur():
    """Crée une instance Chrome headless avec undetected-chromedriver."""
    import shutil

    options = uc.ChromeOptions()
    if not MODE_VISIBLE:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--lang=fr-FR")
    options.add_argument("--remote-debugging-port=9222")

    binaire_possible = None
    for nom in ("google-chrome-stable", "google-chrome", "chromium-browser", "chromium"):
        chemin = shutil.which(nom)
        if chemin:
            binaire_possible = chemin
            break
    if binaire_possible:
        logger.info(f"Binaire Chrome détecté : {binaire_possible}")
        options.binary_location = binaire_possible

    driver = uc.Chrome(options=options, version_main=None, use_subprocess=True)
    driver.set_page_load_timeout(30)
    return driver


def attendre_challenge_cloudflare(driver, essais: int = 3):
    """Attend qu'un éventuel challenge Cloudflare ('Just a moment...') se résolve."""
    for _ in range(essais):
        titre = driver.title.lower()
        if "just a moment" in titre or "attention required" in titre:
            logger.info("  Challenge Cloudflare détecté, attente...")
            time.sleep(4)
        else:
            return True
    return False


def cliquer_voir_plus(driver):
    """
    Clique sur tous les boutons/liens 'Voir plus' de la page (caractéristiques
    ET équipements) pour révéler les champs cachés par défaut.
    """
    try:
        elements = driver.find_elements(
            By.XPATH, "//*[normalize-space(text())='Voir plus']"
        )
        for el in elements:
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", el)
                time.sleep(0.3)
                el.click()
                time.sleep(0.5)
            except (ElementClickInterceptedException, WebDriverException):
                # Si le clic classique échoue (élément masqué/animé), on retente en JS
                try:
                    driver.execute_script("arguments[0].click();", el)
                    time.sleep(0.5)
                except WebDriverException:
                    continue
    except NoSuchElementException:
        pass


# --------------------------------------------------------------------
# ÉTAPE 1 : collecte des URLs d'annonces depuis les pages de résultats
# --------------------------------------------------------------------

def collecter_urls(driver, nb_pages_max: int, objectif_min: int) -> list[str]:
    """Parcourt les pages de résultats et retourne la liste des URLs d'annonces uniques."""
    urls = set()
    pages_vides_consecutives = 0

    for page in range(1, nb_pages_max + 1):
        url = BASE_URL_RECHERCHE if page == 1 else f"{BASE_URL_RECHERCHE}?o={page}"
        logger.info(f"[Étape 1/2] Page de résultats {page}/{nb_pages_max} -> {url}")

        try:
            driver.get(url)
        except TimeoutException:
            logger.error(f"Timeout sur {url}")
            pages_vides_consecutives += 1
            continue

        time.sleep(random.uniform(2.0, 3.5))
        attendre_challenge_cloudflare(driver)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        # Les cartes de la page de résultats et les URLs canoniques des
        # annonces individuelles peuvent utiliser deux formats différents :
        # /voitures_d_occasion/<titre>_<id>.htm OU /voitures/<titre>_<id>.htm
        # On accepte les deux pour ne rien manquer.
        liens = soup.find_all("a", href=re.compile(r"/voitures(?:_d_occasion)?/[^/]+\.htm$"))

        if not liens:
            # Filet de sécurité : peu importe le segment du milieu, une
            # annonce Avito se termine TOUJOURS par "_<identifiant numérique>.htm"
            # (ex: ..._58128799.htm). Ce pattern est beaucoup plus stable que
            # le nom exact du dossier ("voitures", "voitures_d_occasion", etc.)
            liens = soup.find_all("a", href=re.compile(r"_\d{6,}\.htm$"))
            if liens:
                logger.info(f"  (trouvé via le pattern de secours _ID.htm : {len(liens)} lien(s))")

        if not liens and page == 1:
            # Diagnostic : si même la 1re page ne donne aucun lien, on
            # sauvegarde une capture d'écran + le HTML brut pour inspection
            # manuelle (structure du site probablement différente de ce qui
            # est attendu, ou contenu chargé dynamiquement après coup).
            try:
                driver.save_screenshot("debug_page1.png")
                with open("debug_page1.html", "w", encoding="utf-8") as f:
                    f.write(driver.page_source)
                logger.warning(
                    "0 lien trouvé sur la page 1 : capture 'debug_page1.png' et "
                    "'debug_page1.html' sauvegardées pour inspection manuelle."
                )
            except WebDriverException:
                pass
        liens_page = set()
        for lien in liens:
            href = lien.get("href", "")
            if href:
                if not href.startswith("http"):
                    href = "https://www.avito.ma" + href
                liens_page.add(href)

        logger.info(f"  -> {len(liens_page)} lien(s) unique(s) trouvé(s) sur cette page")

        if not liens_page:
            pages_vides_consecutives += 1
            if pages_vides_consecutives >= 3:
                logger.info("3 pages vides consécutives -> fin probable des résultats.")
                break
        else:
            pages_vides_consecutives = 0
            urls.update(liens_page)

        logger.info(f"  Total cumulé : {len(urls)} URLs uniques")

        if len(urls) >= objectif_min * 1.3:
            logger.info("Objectif d'URLs largement atteint, arrêt de la collecte.")
            break

        time.sleep(random.uniform(DELAI_MIN, DELAI_MAX))

    return list(urls)


# --------------------------------------------------------------------
# ÉTAPE 2 : extraction des détails d'une annonce
# --------------------------------------------------------------------

def extraire_valeur_spec(soup: BeautifulSoup, label: str) -> str | None:
    """
    Cherche l'icône <img alt="label"> et récupère la valeur associée.
    Sur Avito, le conteneur de chaque caractéristique contient le texte
    "VALEURLabel" collés (ex: "2022Année-Modèle"). On remonte l'arbre DOM
    depuis l'icône jusqu'à trouver ce conteneur, puis on retire le libellé
    pour ne garder que la valeur.
    """
    img = soup.find("img", alt=label)
    if not img:
        return None

    noeud = img
    for _ in range(5):
        noeud = noeud.parent
        if noeud is None:
            break
        texte = noeud.get_text(strip=True)
        # Le bon conteneur est le plus petit qui contient le libellé
        # complet (pour éviter de remonter jusqu'à toute la page)
        if label in texte and len(texte) < 120:
            valeur = texte.replace(label, "").strip()
            return valeur or None
    return None


def extraire_ville_secteur(soup: BeautifulSoup, url: str) -> tuple[str | None, str | None]:
    """
    Extrait la ville et le secteur.
    IMPORTANT : le segment de localisation dans l'URL (ex: .../fr/massira_2/...)
    correspond tantôt au Secteur, tantôt à la Ville selon ce que le vendeur a
    renseigné — il n'est donc PAS fiable pour déduire la Ville. On utilise en
    priorité les champs structurés "Ville"/"Secteur" de la page (icônes), et
    le fil d'Ariane en repli.
    """
    ville = extraire_valeur_spec(soup, "Ville")
    secteur = extraire_valeur_spec(soup, "Secteur")

    if not ville:
        # Repli : fil d'Ariane (navigation en haut de page)
        for lien in soup.find_all("a", href=re.compile(r"^https://www\.avito\.ma/fr/[a-z_À-ÿ]+$")):
            texte = lien.get_text(strip=True)
            if texte and texte.lower() not in ("accueil", "tout le maroc", "voitures", "véhicules"):
                ville = texte
                break

    return ville, secteur


def extraire_prix(soup: BeautifulSoup) -> int | None:
    """
    Extrait le prix réel de l'annonce, en évitant les pièges classiques :
    - "X DH / mois" (mensualité de financement)
    - "0 DH" (valeur par défaut du simulateur de crédit)
    On cherche d'abord près du titre (h1), qui est la source la plus fiable.
    """
    h1 = soup.find("h1")
    zone_recherche = None
    if h1:
        conteneur = h1
        for _ in range(3):
            if conteneur.parent:
                conteneur = conteneur.parent
        zone_recherche = conteneur.get_text(separator=" ", strip=True)

    textes_a_essayer = [zone_recherche, soup.get_text(separator=" ", strip=True)]

    for texte in textes_a_essayer:
        if not texte:
            continue
        matches = re.findall(r"([\d][\d\s]{2,})\s?DH(?!\s*/\s*mois)(?!\s*Par mois)", texte)
        for m in matches:
            valeur = int(re.sub(r"[^\d]", "", m))
            if valeur >= 1000:  # écarte le "0 DH" du simulateur de crédit
                return valeur
    return None


def extraire_details_annonce(driver, url: str) -> dict | None:
    """Visite une annonce individuelle et en extrait tous les champs."""
    try:
        driver.get(url)
    except TimeoutException:
        logger.error(f"Timeout de chargement pour {url}")
        return None

    time.sleep(random.uniform(2.0, 3.5))
    if not attendre_challenge_cloudflare(driver):
        logger.warning(f"Page probablement bloquée par Cloudflare : {url}")
        return None

    cliquer_voir_plus(driver)

    html = driver.page_source
    if "Année-Modèle" not in html and "Marque" not in html:
        logger.warning(f"Contenu suspect, annonce ignorée : {url}")
        return None

    soup = BeautifulSoup(html, "html.parser")

    resultat = {col: None for col in COLONNES_FINALES}
    resultat["Lien"] = url

    ville, secteur = extraire_ville_secteur(soup, url)
    resultat["Ville"] = ville
    resultat["Secteur"] = secteur

    for champ in CHAMPS_SPEC:
        if champ in ("Ville", "Secteur"):
            continue  # déjà géré ci-dessus par extraire_ville_secteur
        resultat[champ] = extraire_valeur_spec(soup, champ)

    # Conversions numériques (silencieuses si le champ est manquant/mal formé)
    if resultat.get("Année-Modèle"):
        try:
            resultat["Année-Modèle"] = int(re.sub(r"[^\d]", "", resultat["Année-Modèle"])[:4])
        except (ValueError, TypeError):
            pass
    if resultat.get("Kilométrage"):
        try:
            resultat["Kilométrage"] = int(re.sub(r"[^\d]", "", resultat["Kilométrage"]))
        except (ValueError, TypeError):
            pass
    if resultat.get("Puissance fiscale"):
        try:
            resultat["Puissance fiscale"] = int(re.sub(r"[^\d]", "", resultat["Puissance fiscale"]))
        except (ValueError, TypeError):
            pass
    if resultat.get("Nombre de portes"):
        try:
            resultat["Nombre de portes"] = int(re.sub(r"[^\d]", "", resultat["Nombre de portes"]))
        except (ValueError, TypeError):
            pass

    # Équipements : présence de l'icône = True, sinon False
    for equip in CHAMPS_EQUIPEMENTS:
        resultat[equip] = soup.find("img", alt=equip) is not None

    resultat["Prix"] = extraire_prix(soup)

    return resultat


# --------------------------------------------------------------------
# SAUVEGARDE INCRÉMENTALE
# --------------------------------------------------------------------

def sauvegarder_incremental(ligne: dict, fichier: str, ecrire_entete: bool):
    mode = "w" if ecrire_entete else "a"
    with open(fichier, mode, newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=COLONNES_FINALES)
        if ecrire_entete:
            writer.writeheader()
        writer.writerow(ligne)


def binner_kilometrage(km: int) -> str:
    """
    Optionnel : convertit un kilométrage exact en tranche (même format que
    les datasets Avito basés sur les filtres de recherche, ex: '200 000 - 249 999').
    À utiliser en prétraitement si vous avez besoin de ce format précis,
    sinon la valeur exacte (colonne Kilométrage) est préférable pour le ML.
    """
    if km is None:
        return None
    largeur = 5000 if km < 100_000 else 10_000 if km < 300_000 else 50_000
    bas = (km // largeur) * largeur
    haut = bas + largeur - 1
    return f"{bas:,} - {haut:,}".replace(",", " ")


# --------------------------------------------------------------------
# POINT D'ENTRÉE
# --------------------------------------------------------------------

def main():
    logger.info("=== Démarrage du scraping Avito.ma (pages de détail) ===")
    driver = creer_navigateur()

    try:
        # --- Étape 1 : collecte des URLs ---
        logger.info("Échauffement de session (page d'accueil)...")
        try:
            driver.get("https://www.avito.ma/")
            time.sleep(3)
            attendre_challenge_cloudflare(driver)
        except TimeoutException:
            pass

        urls = collecter_urls(driver, NB_PAGES_RECHERCHE_MAX, OBJECTIF_MIN_ANNONCES)
        logger.info(f"[Étape 1/2] Terminée : {len(urls)} URLs collectées.")
        pd.Series(urls, name="url").to_csv(FICHIER_URLS, index=False)

        # --- Reprise automatique : on ignore les annonces déjà scrapées ---
        # Si le script a été interrompu (coupure de courant, PC éteint, etc.),
        # avito_car_dataset.csv contient déjà une partie des résultats. On ne
        # revisite pas ces URLs, ce qui permet de reprendre exactement là où
        # on s'était arrêté au lieu de tout recommencer.
        urls_deja_faites = set()
        if Path(FICHIER_SORTIE).exists():
            try:
                df_existant = pd.read_csv(FICHIER_SORTIE, encoding="utf-8-sig")
                urls_deja_faites = set(df_existant["Lien"].dropna().tolist())
                logger.info(
                    f"Reprise détectée : {len(urls_deja_faites)} annonce(s) déjà "
                    f"présente(s) dans {FICHIER_SORTIE}, elles seront ignorées."
                )
            except (pd.errors.EmptyDataError, KeyError):
                pass

        urls_a_faire = [u for u in urls if u not in urls_deja_faites]
        logger.info(
            f"[Étape 2/2] {len(urls_a_faire)} annonce(s) restante(s) à scraper "
            f"(sur {len(urls)} URLs collectées, {len(urls_deja_faites)} déjà faites)."
        )

        # --- Étape 2 : extraction des détails de chaque annonce ---
        logger.info("[Étape 2/2] Extraction des détails de chaque annonce...")
        fichier_deja_initialise = Path(FICHIER_SORTIE).exists() and len(urls_deja_faites) > 0
        nb_ok, nb_echecs = 0, 0

        for i, url in enumerate(urls_a_faire, 1):
            logger.info(f"[Étape 2/2] Annonce {i}/{len(urls_a_faire)} -> {url}")
            try:
                donnees = extraire_details_annonce(driver, url)
            except WebDriverException as e:
                logger.error(f"Erreur Selenium sur {url} : {e}")
                donnees = None

            if donnees:
                sauvegarder_incremental(
                    donnees, FICHIER_SORTIE, ecrire_entete=not fichier_deja_initialise
                )
                fichier_deja_initialise = True
                nb_ok += 1
            else:
                nb_echecs += 1

            if i % 20 == 0:
                logger.info(f"  Progression : {nb_ok} OK / {nb_echecs} échecs sur {i} annonces")

            time.sleep(random.uniform(DELAI_MIN, DELAI_MAX))

        logger.info(f"Extraction terminée : {nb_ok} annonces OK, {nb_echecs} échecs.")

    finally:
        driver.quit()
        logger.info("Navigateur fermé.")

    if Path(FICHIER_SORTIE).exists():
        df = pd.read_csv(FICHIER_SORTIE, encoding="utf-8-sig")
        logger.info(f"Dataset final : {len(df)} lignes, {len(df.columns)} colonnes.")
        logger.info(f"Sauvegardé dans : {FICHIER_SORTIE}")

        # Export supplémentaire au format Excel (.xlsx)
        fichier_excel = FICHIER_SORTIE.replace(".csv", ".xlsx")
        df.to_excel(fichier_excel, index=False, engine="openpyxl")
        logger.info(f"Version Excel sauvegardée dans : {fichier_excel}")

        if len(df) < OBJECTIF_MIN_ANNONCES:
            logger.warning(
                f"Moins de {OBJECTIF_MIN_ANNONCES} observations. Augmentez "
                "NB_PAGES_RECHERCHE_MAX ou OBJECTIF_MIN_ANNONCES et relancez."
            )


if __name__ == "__main__":
    main()
