def find_gene_orthogroup_simple(gene_id: str) -> str:
    """Simple gene lookup"""
    global _gene_map
    load_orthogroups_data()  # Make sure data is loaded
    return _gene_map.get(gene_id)
