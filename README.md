# 🚗 Analyse intelligente du marché automobile marocain

## 📌 Description

Ce projet propose une analyse intelligente du marché des voitures d'occasion au Maroc à partir d'annonces collectées depuis la plateforme **Avito**.

L'objectif est de construire une solution complète permettant de :

- 🕷️ Collecter automatiquement les annonces automobiles
- 🧹 Nettoyer et préparer les données
- 📊 Réaliser une analyse exploratoire des données (EDA)
- 🤖 Prédire le prix des véhicules
- 📈 Évaluer et optimiser plusieurs modèles de Machine Learning
- 🔍 Identifier les facteurs les plus importants dans la détermination du prix
- 🚘 Segmenter les véhicules selon leurs caractéristiques
- 📱 Visualiser les résultats à travers un dashboard interactif

---

## 🎯 Objectifs du projet

Les principaux objectifs sont :

1. Automatiser la collecte des annonces automobiles.
2. Constituer un dataset représentatif du marché marocain.
3. Nettoyer et préparer les données pour le Machine Learning.
4. Analyser les caractéristiques des véhicules et leur influence sur le prix.
5. Construire des modèles capables d'estimer le prix d'un véhicule.
6. Comparer plusieurs algorithmes de Machine Learning.
7. Optimiser le meilleur modèle avec `GridSearchCV`.
8. Segmenter les véhicules en groupes homogènes avec K-Means.
9. Présenter les résultats à travers un dashboard.

---

## 🏗️ Architecture du projet

```text
                    ┌──────────────────────┐
                    │      Avito.ma        │
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
                    │ Missing values       │
                    │ Doublons             │
                    │ Outliers              │
                    │ Encoding              │
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



