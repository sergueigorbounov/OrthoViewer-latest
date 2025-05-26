# BioSemantic Viz

![BioSemantic Logo](https://via.placeholder.com/150x50?text=BioSemantic)

BioSemantic Viz est une application moderne pour la visualisation et l'analyse de données biologiques, notamment les orthogroupes et les gènes. L'application est construite avec une architecture séparée frontend/backend et suit les principes du développement piloté par les tests (TDD).

## Table des matières

- [Fonctionnalités](#fonctionnalités)
- [Prérequis](#prérequis)
- [Installation](#installation)
- [Structure du projet](#structure-du-projet)
- [Lancement de l'application](#lancement-de-lapplication)
  - [Lancement du backend](#lancement-du-backend)
  - [Lancement du frontend](#lancement-du-frontend)
  - [Lancement complet avec Docker](#lancement-complet-avec-docker)
- [Tests](#tests)
  - [Tests backend](#tests-backend)
  - [Tests frontend](#tests-frontend)
  - [Tests de performance](#tests-de-performance)
- [API Documentation](#api-documentation)
- [Contribution](#contribution)
- [Licence](#licence)

## Fonctionnalités

- Visualisation interactive d'orthogroupes et de gènes
- Recherche performante de gènes (<50ms de temps de réponse)
- Interface utilisateur moderne et réactive
- API RESTful complète
- Dashboard analytique pour explorer les données
- Téléchargement et analyse de fichiers de données biologiques

## Prérequis

- Python 3.9+ (pour le backend)
- Node.js 16+ (pour le frontend)
- Docker et Docker Compose (optionnel, pour le déploiement conteneurisé)
- Conda (recommandé pour gérer les environnements Python)

## Installation

### Cloner le dépôt

```bash
git clone https://github.com/votre-organisation/biosemantic-viz.git
cd biosemantic-viz
```

### Backend

```bash
cd backend

# Option 1: Avec Conda (recommandé)
conda env create -f environment.yml
conda activate biosemantic

# Option 2: Avec virtualenv
python -m venv .venv
source .venv/bin/activate  # Sur Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend-vite
npm install
```

## Structure du projet

```
biosemantic-viz/
├── backend/               # Backend FastAPI
│   ├── app/               # Code source du backend
│   │   ├── api/           # Endpoints API
│   │   ├── core/          # Configuration et utilitaires
│   │   ├── data_access/   # Accès aux données
│   │   ├── models/        # Modèles de données
│   │   └── services/      # Logique métier
│   ├── tests/             # Tests du backend
│   │   ├── api/           # Tests des routes API
│   │   ├── integration/   # Tests d'intégration
│   │   ├── performance/   # Tests de performance
│   │   └── unit/          # Tests unitaires
│   ├── environment.yml    # Environnement Conda
│   └── requirements.txt   # Dépendances Python
│
├── frontend-vite/         # Frontend Vite/React
│   ├── public/            # Fichiers statiques
│   ├── src/               # Code source du frontend
│   │   ├── api/           # Clients API
│   │   ├── components/    # Composants React
│   │   ├── pages/         # Pages/écrans
│   │   └── utils/         # Utilitaires
│   ├── package.json       # Dépendances Node.js
│   └── vite.config.ts     # Configuration Vite
│
├── docker-compose.yml     # Configuration Docker Compose
├── docker-compose.dev.yml # Configuration Docker pour développement
└── run-app.sh             # Script principal pour exécuter l'application
```

## Lancement de l'application

Plusieurs options sont disponibles pour lancer l'application:

### Lancement du backend

```bash
# Option 1: Utiliser le script TDD
cd backend
./tdd.sh start

# Option 2: Lancer directement avec uvicorn
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 3: Utiliser le script principal
./run-app.sh backend
```

Le backend sera accessible à l'adresse [http://localhost:8000](http://localhost:8000)

### Lancement du frontend

```bash
# Option 1: Utiliser le script TDD
cd frontend-vite
./tdd.sh start

# Option 2: Lancer directement avec npm
cd frontend-vite
npm run dev

# Option 3: Utiliser le script principal
./run-app.sh frontend
```

Le frontend sera accessible à l'adresse [http://localhost:3000](http://localhost:3000)

### Lancement complet avec Docker

```bash
# Production
./run-app.sh docker

# Développement (avec hot reload)
./run-app.sh docker-dev
```

Avec Docker, l'application complète sera accessible à l'adresse [http://localhost](http://localhost)

## Tests

Notre application suit les principes du Test-Driven Development (TDD). Voici comment exécuter les différents types de tests:

### Tests backend

```bash
cd backend

# Exécuter tous les tests
./run_tests.sh

# Exécuter des types de tests spécifiques
./run_tests.sh unit          # Tests unitaires
./run_tests.sh integration   # Tests d'intégration
./run_tests.sh api           # Tests API
./run_tests.sh performance   # Tests de performance
./run_tests.sh fuzzing       # Tests de fuzzing
```

### Tests frontend

```bash
cd frontend-vite

# Exécuter tous les tests
npm test

# Exécuter les tests en mode watch
npm test -- --watch

# Générer un rapport de couverture
npm test -- --coverage
```

### Tests de performance

Nous avons implémenté des tests de performance spécifiques pour garantir que les recherches de gènes s'exécutent en moins de 50ms:

```bash
cd backend
./run_tests.sh performance
```

## API Documentation

La documentation Swagger de l'API est disponible aux adresses suivantes lorsque le backend est en cours d'exécution:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Endpoints API principaux

| Endpoint | Méthode | Description |
|----------|---------|-------------|
| `/api/species` | GET | Récupérer toutes les espèces |
| `/api/species/{species_id}` | GET | Récupérer une espèce par ID |
| `/api/orthogroups` | GET | Récupérer tous les orthogroupes |
| `/api/orthogroup/{og_id}` | GET | Récupérer un orthogroupe par ID |
| `/api/genes` | GET | Récupérer tous les gènes |
| `/api/gene/{gene_id}` | GET | Récupérer un gène par ID |
| `/api/genes/search` | GET | Rechercher des gènes par nom ou ID |
| `/api/dashboard/stats` | GET | Récupérer des statistiques pour le dashboard |
| `/api/upload` | POST | Télécharger un fichier de données |
| `/api/visualize` | POST | Créer une visualisation |

## Contribution

Nous accueillons les contributions! Voici comment vous pouvez contribuer:

1. Forker le projet
2. Créer une branche pour votre fonctionnalité (`git checkout -b feature/amazing-feature`)
3. Commiter vos changements (`git commit -m 'Add some amazing feature'`)
4. Pousser vers la branche (`git push origin feature/amazing-feature`)
5. Ouvrir une Pull Request

Veuillez vous assurer que vos contributions suivent nos standards de code et que tous les tests passent.

## Développement TDD

Pour développer de nouvelles fonctionnalités en suivant l'approche TDD:

1. Écrire un test qui échoue décrivant la fonctionnalité attendue
2. Implémenter le minimum de code pour faire passer le test
3. Refactoriser le code tout en maintenant les tests au vert
4. Répéter le processus pour enrichir la fonctionnalité

## Licence

Distribué sous la licence XYZ. Voir `LICENSE` pour plus d'informations.

## Contact

Votre Nom - [@votre_twitter](https://twitter.com/votre_twitter) - email@example.com

Lien du projet: [https://github.com/votre-organisation/biosemantic-viz](https://github.com/votre-organisation/biosemantic-viz)