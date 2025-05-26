# Architecture du Backend

Ce document explique l'architecture en couches du backend de l'application.

## Vue d'ensemble

L'application utilise une architecture en trois couches principales :

1. **Couche API (api)** : Gère les requêtes HTTP et les réponses.
2. **Couche Service (services)** : Contient la logique métier et coordonne les opérations.
3. **Couche Accès aux Données (data_access)** : Responsable de l'accès et de la manipulation des données.

En plus de ces trois couches principales, nous avons :

4. **Couche Core (core)** : Contient la configuration et les utilitaires communs.
5. **Couche Modèles (models)** : Définit les structures de données utilisées dans l'application.

## Structure des répertoires

```
backend/
├── app/
│   ├── api/                # Couche API
│   │   ├── routes/         # Routes organisées par domaine
│   │   └── ...
│   ├── services/           # Couche Service (logique métier)
│   │   ├── orthologue_service.py
│   │   ├── ete_tree_service.py
│   │   └── ...
│   ├── data_access/        # Couche Accès aux Données
│   │   ├── orthogroups_repository.py
│   │   ├── species_repository.py
│   │   └── ...
│   ├── core/               # Configuration et utilitaires
│   │   ├── config.py
│   │   └── ...
│   ├── models/             # Modèles de données (Pydantic)
│   │   ├── phylo.py
│   │   └── ...
│   └── main.py             # Point d'entrée de l'application
├── tests/                  # Tests
└── ...
```

## Couches de l'application

### 1. Couche API (api)

Cette couche est responsable de :
- Définir les endpoints de l'API REST
- Valider les données de requête
- Déléguer le traitement aux services
- Formater les réponses

Exemple de code :
```python
@router.post("/search", response_model=OrthologueSearchResponse)
async def search_orthologues(request: OrthologueSearchRequest):
    """Search for orthologues of a given gene."""
    return await orthologue_service.search_orthologues(request)
```

### 2. Couche Service (services)

Cette couche contient la logique métier et est responsable de :
- Coordonner les opérations entre différents repositories
- Appliquer les règles métier
- Transformer les données selon les besoins
- Gérer les erreurs métier

Exemple de code :
```python
async def search_orthologues(self, request: OrthologueSearchRequest):
    """Search for orthologues of a given gene."""
    gene_id = request.gene_id.strip()
    
    # Find the orthogroup for the gene
    orthogroup_id = self.orthogroups_repo.find_gene_orthogroup(gene_id)
    
    # Get all genes in the orthogroup
    genes_by_species = self.orthogroups_repo.get_orthogroup_genes(orthogroup_id)
    
    # Process results...
    # ...
```

### 3. Couche Accès aux Données (data_access)

Cette couche est responsable de :
- Accéder aux sources de données (fichiers, API externes, etc.)
- Exécuter des requêtes et manipuler les données
- Convertir les données brutes en objets métier
- Gérer la persistance des données

Exemple de code :
```python
def find_gene_orthogroup(self, gene_id: str) -> Optional[str]:
    """Find orthogroup ID for a given gene."""
    # Make sure data is loaded
    self.load_orthogroups_data()
    
    # Direct lookup in the gene map
    return self._gene_map.get(gene_id)
```

### 4. Couche Core (core)

Cette couche contient :
- Configuration de l'application
- Utilitaires communs
- Initialisation des composants essentiels

### 5. Couche Modèles (models)

Cette couche définit :
- Structures de données (modèles Pydantic)
- Validation des données
- Schémas de requête et de réponse

## Flux de données

1. Les requêtes HTTP entrent dans l'application via les routes API
2. Les routes délèguent le traitement aux services appropriés
3. Les services utilisent les repositories pour accéder aux données
4. Les repositories récupèrent, manipulent et retournent les données
5. Les services appliquent la logique métier et transforment les données
6. Les routes renvoient les réponses aux clients

## Avantages de cette architecture

- **Séparation des préoccupations** : Chaque couche a une responsabilité unique
- **Testabilité** : Facilite l'écriture de tests unitaires pour chaque couche
- **Maintenabilité** : Les modifications dans une couche n'affectent pas les autres
- **Évolutivité** : Facilite l'ajout de nouvelles fonctionnalités
- **Lisibilité** : Organisation claire du code