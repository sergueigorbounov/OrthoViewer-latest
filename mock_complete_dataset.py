#!/usr/bin/env python3
"""
🧬 MOCK COMPLETE DATASET
Crée un dataset complet avec les gènes d'exemple pour tester le chunked search
"""

import json
import os
from typing import Dict, List, Any

def create_comprehensive_gene_dataset() -> Dict[str, Any]:
    """Crée un dataset complet avec les gènes d'exemple et plus"""
    
    # Gènes d'exemple mentionnés dans l'UI
    example_genes = [
        {
            "id": "AT1G01010.1",
            "name": "NAC domain transcription factor",
            "species_id": "Ath",
            "orthogroup_id": "OG0000001",
            "description": "NAC transcription factor family member",
            "go_terms": [
                {"id": "GO:0003700", "name": "DNA-binding transcription factor activity", "category": "Molecular Function"},
                {"id": "GO:0006355", "name": "regulation of transcription", "category": "Biological Process"}
            ]
        },
        {
            "id": "Cma_005726",
            "name": "Cucurbita maxima gene",
            "species_id": "Cma", 
            "orthogroup_id": "OG0000002",
            "description": "Cucurbita maxima annotated gene",
            "go_terms": [
                {"id": "GO:0005634", "name": "nucleus", "category": "Cellular Component"}
            ]
        },
        {
            "id": "Aco000536.1",
            "name": "Ananas comosus gene",
            "species_id": "Aco",
            "orthogroup_id": "OG0000003", 
            "description": "Pineapple annotated gene",
            "go_terms": []
        },
        {
            "id": "Traes_4AL_F00707FAF.1",
            "name": "Triticum aestivum gene",
            "species_id": "Tra",
            "orthogroup_id": "OG0000004",
            "description": "Wheat annotated gene",
            "go_terms": [
                {"id": "GO:0009765", "name": "photosynthesis", "category": "Biological Process"}
            ]
        }
    ]
    
    # Générer plus de gènes AT pour les tests
    at_genes = []
    for i in range(1, 301):  # 300 gènes AT
        at_genes.append({
            "id": f"AT1G{i:05d}",
            "name": f"Arabidopsis gene {i}",
            "species_id": "Ath",
            "orthogroup_id": f"OG{i:07d}",
            "description": f"Arabidopsis thaliana gene {i}",
            "go_terms": [
                {"id": f"GO:{1000000+i:07d}", "name": f"Function {i}", "category": "Molecular Function"}
            ] if i % 3 == 0 else []
        })
    
    # Gènes d'autres espèces
    other_genes = [
        {
            "id": "BRCA1",
            "name": "Breast cancer 1",
            "species_id": "Hsa",
            "orthogroup_id": "OG0000100",
            "description": "Tumor suppressor gene",
            "go_terms": [
                {"id": "GO:0004842", "name": "ubiquitin-protein transferase activity", "category": "Molecular Function"},
                {"id": "GO:0006281", "name": "DNA repair", "category": "Biological Process"}
            ]
        },
        {
            "id": "BRCA2", 
            "name": "Breast cancer 2",
            "species_id": "Hsa",
            "orthogroup_id": "OG0000101",
            "description": "DNA repair associated gene",
            "go_terms": [
                {"id": "GO:0003677", "name": "DNA binding", "category": "Molecular Function"}
            ]
        }
    ]
    
    # Combiner tous les gènes
    all_genes = example_genes + at_genes + other_genes
    
    return {
        "genes": all_genes,
        "total_count": len(all_genes),
        "species_count": len(set(gene["species_id"] for gene in all_genes)),
        "orthogroup_count": len(set(gene["orthogroup_id"] for gene in all_genes))
    }

def create_species_dataset() -> Dict[str, Any]:
    """Crée un dataset d'espèces correspondant"""
    species = [
        {"id": "Ath", "name": "Arabidopsis thaliana", "kingdom": "Plantae"},
        {"id": "Cma", "name": "Cucurbita maxima", "kingdom": "Plantae"},
        {"id": "Aco", "name": "Ananas comosus", "kingdom": "Plantae"},
        {"id": "Tra", "name": "Triticum aestivum", "kingdom": "Plantae"},
        {"id": "Hsa", "name": "Homo sapiens", "kingdom": "Animalia"}
    ]
    
    return {"species": species}

def create_orthogroups_dataset() -> Dict[str, Any]:
    """Crée un dataset d'orthogroupes"""
    orthogroups = []
    
    # Orthogroupes pour les gènes d'exemple
    example_ogs = [
        {"id": "OG0000001", "name": "NAC transcription factors", "species": ["Ath"]},
        {"id": "OG0000002", "name": "Cucurbita gene family", "species": ["Cma"]},
        {"id": "OG0000003", "name": "Pineapple gene family", "species": ["Aco"]},
        {"id": "OG0000004", "name": "Wheat gene family", "species": ["Tra"]},
        {"id": "OG0000100", "name": "BRCA family", "species": ["Hsa"]},
        {"id": "OG0000101", "name": "DNA repair family", "species": ["Hsa"]}
    ]
    
    orthogroups.extend(example_ogs)
    
    # Générer plus d'orthogroupes
    for i in range(1, 301):
        orthogroups.append({
            "id": f"OG{i:07d}",
            "name": f"Orthogroup {i}",
            "species": ["Ath"]  # Principalement Arabidopsis
        })
    
    return {"orthogroups": orthogroups}

def save_mock_datasets():
    """Sauvegarde tous les datasets mock"""
    
    # Créer le répertoire de données si nécessaire
    data_dir = "backend/data"
    os.makedirs(data_dir, exist_ok=True)
    
    # Générer et sauvegarder les datasets
    datasets = {
        "genes.json": create_comprehensive_gene_dataset(),
        "species.json": create_species_dataset(), 
        "orthogroups.json": create_orthogroups_dataset()
    }
    
    for filename, data in datasets.items():
        filepath = os.path.join(data_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Saved {filepath}")
        print(f"   - Records: {len(data[list(data.keys())[0]])}")
    
    print(f"\n🎯 MOCK DATASET CREATED:")
    print(f"- Example genes: AT1G01010.1, Cma_005726, etc. ✅")
    print(f"- Total genes: {len(datasets['genes.json']['genes'])}")
    print(f"- AT genes for testing: 300+")
    print(f"- Species: {len(datasets['species.json']['species'])}")
    
    return datasets

def main():
    print("🧬 Creating comprehensive mock dataset...")
    
    datasets = save_mock_datasets()
    
    print("\n🔬 TESTING EXAMPLES:")
    gene_data = datasets["genes.json"]
    
    # Vérifier que les gènes d'exemple existent
    example_ids = ["AT1G01010.1", "Cma_005726", "Aco000536.1", "Traes_4AL_F00707FAF.1"]
    
    for example_id in example_ids:
        found = any(gene["id"] == example_id for gene in gene_data["genes"])
        status = "✅" if found else "❌"
        print(f"{status} {example_id}")
    
    print(f"\n🚀 Ready for chunked search testing!")
    print(f"📁 Data files saved to: backend/data/")

if __name__ == "__main__":
    main() 