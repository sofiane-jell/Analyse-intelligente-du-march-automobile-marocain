# 🚗 Analyse intelligente du marché automobile marocain

## 📌 Description

Ce projet propose une analyse intelligente du marché des voitures d'occasion au Maroc à partir d'annonces collectées depuis la plateforme **Avito**.

L'objectif est de construire une solution complète permettant de :

* 🕷️ Collecter automatiquement les annonces automobiles
* 🧹 Nettoyer et préparer les données
* 📊 Réaliser une analyse exploratoire des données (EDA)
* 🤖 Prédire le prix des véhicules
* 📈 Évaluer et optimiser plusieurs modèles de Machine Learning
* 🔍 Identifier les facteurs les plus importants dans la détermination du prix
* 🚘 Segmenter les véhicules selon leurs caractéristiques
* 📱 Visualiser les résultats à travers un dashboard interactif

---

## 🎯 Objectifs du projet

Les principaux objectifs sont :

1. Automatiser la collecte des annonces automobiles.
2. Constituer un dataset représentatif du marché marocain.
3. Nettoyer et préparer les données pour le Machine Learning.
4. Analyser les caractéristiques des véhicules et leur influence sur le prix.
5. Construire des modèles capables d'estimer le prix d'un véhicule.
6. Comparer plusieurs algorithmes de Machine Learning.
7. Optimiser le modèle avec `GridSearchCV`.
8. Segmenter les véhicules en groupes homogènes avec K-Means.
9. Présenter les résultats à travers un dashboard interactif.

---

## 🏗️ Architecture du projet

```text
                    ┌──────────────────────┐
                    │       Avito.ma       │
                    │  Annonces voitures   │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       Scraping       │
                    │ Selenium + Beautiful │
                    │ Soup + ChromeDriver  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       Dataset        │
                    │        CSV           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    Prétraitement     │
                    │ Valeurs manquantes   │
                    │ Doublons             │
                    │ Valeurs aberrantes   │
                    │ Encodage             │
                    │ Standardisation      │
                    └──────────┬───────────┘
                               │
                 ┌─────────────┴─────────────┐
                 ▼                           ▼
        ┌─────────────────┐         ┌─────────────────┐
        │       EDA       │         │ Machine Learning│
        │ Analyse données │         │ Prédiction prix │
        └─────────────────┘         └────────┬────────┘
                                             │
                           ┌─────────────────┼─────────────────┐
                           ▼                 ▼                 ▼
                    Linear Regression   Random Forest      XGBoost
                                             │
                                             ▼
                                      GridSearchCV
                                             │
                                             ▼
                                      Modèle final
                                             │
                           ┌─────────────────┴─────────────────┐
                           ▼                                   ▼
                    Prédiction prix                     K-Means
                                                               │
                                                               ▼
                                                        Segmentation
                                                               │
                                                               ▼
                                                          Dashboard
```

---

## 📂 Structure du projet

```text
analyse-marche-automobile-marocain/
│
├── data/
│   └── annonces_avito_voitures.csv
│
├── notebooks/
│   └── analyse_marche_automobile.ipynb
│
├── scraping/
│   └── scraping_avito.py
│
├── dashboard/
│   └── app.py
│
├── models/
│   └── model_random_forest.pkl
│
├── requirements.txt
├── README.md
└── Rapport_Projet_avito_MLA.pdf
```

---

# 🛠️ Technologies utilisées

### Langage

* Python

### Web Scraping

* Selenium
* Undetected ChromeDriver
* BeautifulSoup
* Requests
* Regex (`re`)

### Data Science

* Pandas
* NumPy
* Matplotlib
* Seaborn

### Machine Learning

* Scikit-learn
* XGBoost

### Visualisation

* Matplotlib
* Seaborn
* Dashboard interactif

### Outils

* Jupyter Notebook
* Git
* GitHub

---

# 📊 Dataset

Le dataset initial contient :

* **5 242 annonces**
* **31 variables**

Après le nettoyage et le prétraitement :

* **5 032 annonces**
* Environ **96 % des données conservées**

Les principales variables comprennent :

* Prix
* Marque
* Modèle
* Année-Modèle
* Kilométrage
* Carburant
* Boîte de vitesses
* Ville
* Puissance fiscale
* Nombre de portes
* Nombre d'équipements

---

# 🕷️ Web Scraping

La collecte des données est réalisée automatiquement à l'aide de Python.

Les principales bibliothèques utilisées sont :

* Selenium
* undetected-chromedriver
* BeautifulSoup
* pandas
* csv
* pathlib
* re
* logging

Le scraping est organisé en deux étapes principales :

```text
1. Collecte des URLs des annonces
                ↓
2. Extraction des informations de chaque annonce
```

Le système permet également :

* La sauvegarde progressive des données.
* La reprise du scraping après une interruption.
* La détection des annonces déjà collectées.
* L'enregistrement des résultats dans un fichier CSV.

---

# 🧹 Prétraitement des données

Plusieurs étapes ont été réalisées avant l'entraînement des modèles.

## 1. Gestion des valeurs manquantes

Pour les variables numériques :

```text
Remplacement par la médiane
```

Pour les variables catégorielles :

```text
Remplacement par la valeur la plus fréquente
```

## 2. Suppression des doublons

Les doublons sont identifiés principalement à partir du lien de l'annonce :

```text
Lien
```

## 3. Suppression des valeurs aberrantes

Les limites suivantes ont été utilisées :

```text
Prix          : 20 000 – 3 000 000 DH
Kilométrage   : 0 – 500 000 km
Année         : 1980 – 2026
```

## 4. Encodage

Les variables catégorielles sont transformées avec :

```python
OneHotEncoder
```

## 5. Standardisation

Les variables numériques sont standardisées avec :

```python
StandardScaler
```

## 6. Nombre d'équipements

Une variable supplémentaire est calculée à partir des différents équipements du véhicule :

```text
Nombre équipements
```

---

# 📈 Analyse exploratoire des données

L'analyse exploratoire permet d'étudier :

* La distribution des prix.
* La distribution du kilométrage.
* Les marques les plus représentées.
* La distribution des carburants.
* Le prix médian par marque.
* Les relations entre les variables numériques.
* Les valeurs aberrantes.

### Résultats principaux

```text
Nombre d'annonces nettoyées : 5 032
Prix médian                  : 115 000 DH
Kilométrage médian           : 125 000 km
Marque la plus représentée   : Volkswagen
```

---

# 🤖 Machine Learning

L'objectif principal est de prédire le prix d'une voiture d'occasion.

Trois modèles ont été étudiés :

### 1. Linear Regression

Régression linéaire permettant de modéliser la relation entre les caractéristiques des véhicules et leur prix.

### 2. Random Forest

Random Forest Regressor permettant de capturer des relations non linéaires entre les variables.

### 3. XGBoost

XGBRegressor basé sur une méthode de boosting permettant de construire progressivement un modèle performant.

---

# 📊 Évaluation des modèles

Les métriques utilisées sont :

### MAE

**Mean Absolute Error**

Mesure l'erreur absolue moyenne entre les prix réels et les prix prédits.

### RMSE

**Root Mean Squared Error**

Mesure l'erreur quadratique moyenne en donnant davantage de poids aux grandes erreurs.

### R²

**Coefficient de détermination**

Mesure la capacité du modèle à expliquer la variance des prix.

---

## Résultats initiaux

| Modèle            |  MAE (DH) |  RMSE (DH) |   R² |
| ----------------- | --------: | ---------: | ---: |
| Random Forest     | 37 554.55 | 118 172.63 | 0.53 |
| XGBoost           | 38 541.66 | 116 815.75 | 0.54 |
| Linear Regression | 36 965.03 | 122 117.96 | 0.50 |

---

# 🔄 Validation croisée

Une validation croisée a également été réalisée afin d'obtenir une évaluation plus robuste des modèles.

| Modèle            | MAE moyen (DH) |
| ----------------- | -------------: |
| Linear Regression |      39 143.78 |
| XGBoost           |      40 540.11 |
| Random Forest     |      41 465.37 |

---

# ⚙️ Optimisation avec GridSearchCV

Une optimisation des hyperparamètres du modèle Random Forest a été réalisée avec `GridSearchCV`.

Les meilleurs paramètres obtenus sont :

```python
n_estimators = 60
max_depth = 15
```

Le modèle final obtient les performances suivantes :

| Métrique |      Résultat |
| -------- | ------------: |
| MAE      |  35 627.69 DH |
| RMSE     | 116 404.72 DH |
| R²       |        0.5432 |

---

# 🏆 Modèle final

Le modèle retenu après optimisation est :

**Random Forest Regressor**

avec les paramètres :

```python
n_estimators = 60
max_depth = 15
```

Le modèle obtient une erreur absolue moyenne d'environ :

```text
35 628 DH
```

---

# 🔍 Importance des variables

L'analyse de l'importance des variables montre les résultats suivants :

| Variable           | Importance |
| ------------------ | ---------: |
| Boîte de vitesses  |   0.329754 |
| Année-Modèle       |   0.311517 |
| Puissance fiscale  |   0.091580 |
| Modèle             |   0.080758 |
| Marque             |   0.057081 |
| Nombre équipements |   0.046662 |
| Ville              |   0.035056 |
| Kilométrage        |   0.029135 |
| Carburant          |   0.017809 |
| Nombre de portes   |   0.000648 |

Les variables les plus importantes sont donc principalement :

1. Boîte de vitesses
2. Année-Modèle
3. Puissance fiscale
4. Modèle
5. Marque

---

# 🚘 Segmentation des véhicules

Une segmentation des véhicules a été réalisée avec l'algorithme **K-Means**.

Les variables utilisées sont :

```python
[
    "Prix",
    "Année-Modèle",
    "Kilométrage",
    "Puissance fiscale",
    "Nombre équipements"
]
```

Les données ont été standardisées avant l'application de K-Means.

---

# 📐 Silhouette Score

Les résultats obtenus sont :

| Nombre de clusters | Silhouette Score |
| -----------------: | ---------------: |
|                  2 |           0.4494 |
|                  3 |           0.3064 |
|                  4 |           0.3148 |

Le meilleur résultat est obtenu avec :

```text
k = 2
```

avec un Silhouette Score de :

```text
0.4494
```

---

# 📊 Interprétation des clusters

## Cluster 0

```text
Nombre de véhicules : 594
Prix moyen          : 444 581.65 DH
Année moyenne       : 2020.42
Kilométrage moyen   : 89 574.89 km
Puissance moyenne   : 8.85 CV
Équipements moyens  : 12.4
```

Ce cluster correspond principalement à des véhicules :

* Plus récents
* Plus chers
* Moins kilométrés
* Plus équipés

## Cluster 1

```text
Nombre de véhicules : 4 438
Prix moyen          : 125 573.91 DH
Année moyenne       : 2012.49
Kilométrage moyen   : 134 910.02 km
Puissance moyenne   : 7.18 CV
Équipements moyens  : 2.72
```

Ce cluster correspond principalement à des véhicules :

* Plus anciens
* Moins chers
* Plus kilométrés
* Moins équipés

---

# 🔮 Exemple de prédiction

Pour un véhicule ayant les caractéristiques suivantes :

| Caractéristique      | Valeur     |
| -------------------- | ---------- |
| Marque               | Dacia      |
| Modèle               | Duster     |
| Année                | 2021       |
| Kilométrage          | 65 000 km  |
| Puissance fiscale    | 7 CV       |
| Nombre de portes     | 5          |
| Nombre d'équipements | 10         |
| Ville                | Casablanca |
| Carburant            | Diesel     |
| Boîte de vitesses    | Manuelle   |

Le modèle estime le prix à environ :

```text
175 787.67 DH
```

---

# 📱 Dashboard

Un dashboard permet de visualiser les principales informations du dataset.

Les visualisations comprennent notamment :

* Top des marques.
* Prix médian par marque.
* Distribution des carburants.
* Distribution des prix.
* Distribution du kilométrage.
* Statistiques générales du marché.

---

# 🚀 Installation

## 1. Cloner le projet

```bash
git clone https://github.com/votre-utilisateur/analyse-marche-automobile-marocain.git
```

## 2. Accéder au projet

```bash
cd analyse-marche-automobile-marocain
```

## 3. Créer un environnement virtuel

### Windows

```bash
python -m venv venv
```

### Linux / macOS

```bash
python3 -m venv venv
```

## 4. Activer l'environnement

### Windows

```bash
venv\Scripts\activate
```

### Linux / macOS

```bash
source venv/bin/activate
```

## 5. Installer les dépendances

```bash
pip install -r requirements.txt
```

---

# ▶️ Utilisation

## Lancer le notebook

```bash
jupyter notebook
```

Puis ouvrir :

```text
notebooks/analyse_marche_automobile.ipynb
```

## Lancer le scraping

```bash
python scraping/scraping_avito.py
```

## Lancer le dashboard

Si le dashboard utilise Streamlit :

```bash
streamlit run dashboard/app.py
```

---

# 📦 Requirements

Les principales dépendances utilisées sont :

```text
pandas
numpy
scikit-learn
xgboost
matplotlib
seaborn
selenium
undetected-chromedriver
beautifulsoup4
jupyter
streamlit
joblib
```

---

# ⚠️ Limitations

Le projet présente certaines limites :

* Les prix correspondent aux prix affichés dans les annonces et non nécessairement aux prix réellement négociés.
* Certaines informations mécaniques peuvent être absentes.
* L'historique d'entretien n'est pas disponible.
* Les informations concernant les accidents peuvent être manquantes.
* Certaines marques et certains segments haut de gamme sont moins représentés.
* Le scraping dépend de la structure HTML de la plateforme source.
* Les résultats peuvent évoluer avec l'évolution du marché automobile.

---

# 🔮 Perspectives

Plusieurs améliorations peuvent être envisagées :

* Ajouter davantage de données provenant de différentes plateformes.
* Ajouter l'analyse des descriptions textuelles.
* Exploiter les images des véhicules.
* Ajouter des informations sur l'état mécanique.
* Intégrer l'historique d'entretien.
* Tester d'autres modèles de Machine Learning.
* Effectuer une recherche plus large des hyperparamètres.
* Développer une application Web complète.
* Mettre automatiquement à jour le dataset.
* Déployer le modèle sur un serveur Cloud.

---

# 📚 Rapport

Le rapport complet du projet est disponible dans :

```text
Rapport_Projet_avito_MLA.pdf
```

---

# 👨‍💻 Auteur

**Sofiane Jellouli**

Projet académique — Analyse intelligente du marché automobile marocain.

---

# 🔄 Pipeline du projet

```text
Scraping
    ↓
Collecte des annonces
    ↓
Sauvegarde CSV
    ↓
Nettoyage
    ↓
Prétraitement
    ↓
Analyse exploratoire
    ↓
Feature Engineering
    ↓
Machine Learning
    ↓
Évaluation
    ↓
GridSearchCV
    ↓
Modèle final
    ↓
Prédiction des prix
    ↓
K-Means
    ↓
Segmentation
    ↓
Dashboard
```

---

# ⭐ Résumé

Ce projet met en œuvre une chaîne complète de Data Science appliquée au marché automobile marocain :

```text
Web Scraping
     +
Data Cleaning
     +
Exploratory Data Analysis
     +
Machine Learning
     +
Hyperparameter Optimization
     +
Price Prediction
     +
Vehicle Clustering
     +
Dashboard
```

L'objectif final est de fournir une meilleure compréhension du marché des voitures d'occasion au Maroc et de proposer une estimation automatique du prix des véhicules à partir de leurs caractéristiques.

---

# 📄 Licence

Ce projet est réalisé dans un cadre académique et peut être utilisé à des fins d'apprentissage et de recherche.
