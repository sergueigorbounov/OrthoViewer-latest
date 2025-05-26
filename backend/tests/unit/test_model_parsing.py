import pytest
from pydantic import ValidationError

from app.models.biological_models import Species, OrthoGroup, Gene, GeneByOrthogroup

# Test Species model
def test_species_model_valid():
    """Test creation of a valid Species model."""
    species_data = {
        "id": "sp1",
        "name": "Species 1",
        "taxonomy": "Kingdom;Phylum;Class;Order;Family;Genus;Species"
    }
    
    species = Species(**species_data)
    
    assert species.id == "sp1"
    assert species.name == "Species 1"
    assert species.taxonomy == "Kingdom;Phylum;Class;Order;Family;Genus;Species"

def test_species_model_missing_fields():
    """Test Species model with missing required fields."""
    # Missing name
    species_data = {
        "id": "sp1",
        "taxonomy": "Kingdom;Phylum;Class;Order;Family;Genus;Species"
    }
    
    with pytest.raises(ValidationError):
        Species(**species_data)

# Test OrthoGroup model
def test_orthogroup_model_valid():
    """Test creation of a valid OrthoGroup model."""
    og_data = {
        "id": "OG0001",
        "name": "Orthogroup 1",
        "species": ["sp1", "sp2"],
        "gene_count": 5
    }
    
    og = OrthoGroup(**og_data)
    
    assert og.id == "OG0001"
    assert og.name == "Orthogroup 1"
    assert og.species == ["sp1", "sp2"]
    assert og.gene_count == 5

def test_orthogroup_model_optional_fields():
    """Test OrthoGroup model with optional fields."""
    # Missing gene_count
    og_data = {
        "id": "OG0001",
        "name": "Orthogroup 1",
        "species": ["sp1", "sp2"]
    }
    
    og = OrthoGroup(**og_data)
    
    assert og.id == "OG0001"
    assert og.name == "Orthogroup 1"
    assert og.species == ["sp1", "sp2"]
    assert og.gene_count is None

def test_orthogroup_model_invalid_fields():
    """Test OrthoGroup model with invalid field types."""
    # Invalid species (should be a list)
    og_data = {
        "id": "OG0001",
        "name": "Orthogroup 1",
        "species": "sp1",  # This should be a list
        "gene_count": 5
    }
    
    with pytest.raises(ValidationError):
        OrthoGroup(**og_data)

# Test Gene model
def test_gene_model_valid():
    """Test creation of a valid Gene model."""
    gene_data = {
        "id": "gene1",
        "name": "Gene 1",
        "species_id": "sp1",
        "orthogroup_id": "OG0001",
        "go_terms": [
            {"id": "GO:0001", "name": "Term 1", "category": "Molecular Function"}
        ]
    }
    
    gene = Gene(**gene_data)
    
    assert gene.id == "gene1"
    assert gene.name == "Gene 1"
    assert gene.species_id == "sp1"
    assert gene.orthogroup_id == "OG0001"
    assert len(gene.go_terms) == 1
    assert gene.go_terms[0].id == "GO:0001"

def test_gene_model_without_go_terms():
    """Test Gene model without GO terms."""
    gene_data = {
        "id": "gene1",
        "name": "Gene 1",
        "species_id": "sp1",
        "orthogroup_id": "OG0001",
        "go_terms": []
    }
    
    gene = Gene(**gene_data)
    
    assert gene.id == "gene1"
    assert gene.name == "Gene 1"
    assert gene.species_id == "sp1"
    assert gene.orthogroup_id == "OG0001"
    assert len(gene.go_terms) == 0

# Test GeneByOrthogroup model
def test_gene_by_orthogroup_model_valid():
    """Test creation of a valid GeneByOrthogroup model."""
    data = {
        "name": "Orthogroup 1",
        "genes": 5
    }
    
    model = GeneByOrthogroup(**data)
    
    assert model.name == "Orthogroup 1"
    assert model.genes == 5