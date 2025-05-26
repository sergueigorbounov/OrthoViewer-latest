import logging
import re

logger = logging.getLogger(__name__)

def get_species_full_name(species_id, species_mapping):
    """Get the full species name from the mapping, trying different matching strategies"""
    # Strip any numbers or special characters for the initial lookup
    clean_id = re.sub(r'[0-9\(\)\[\]\{\}]', '', species_id).strip()
    
    # Try exact match first
    if clean_id in species_mapping['id_to_full']:
        return species_mapping['id_to_full'][clean_id]
    
    # Try prefix matching for IDs like "At3g01090"
    for prefix, full_name in species_mapping['prefix_to_full'].items():
        if clean_id.startswith(prefix):
            logger.info(f"Found prefix match for {species_id} -> {full_name} (prefix: {prefix})")
            return full_name
    
    # Manual mapping for specific cases we see in the UI
    ui_abbreviations = {
        'Bju': 'Brassica juncea',
        'Gm': 'Glycine max',
        'Ma': 'Musa acuminata',
        'Nt': 'Nicotiana tabacum',
        'Md': 'Malus domestica',
        'Pvi': 'Panicum virgatum',
        'Bni': 'Brassica nigra',
        'Bo': 'Brassica oleracea',
        'Ms': 'Medicago sativa',
        'Rnc': 'Raphanus sativus',
        'Ha': 'Helianthus annuus',
        'Bna': 'Brassica napus',
        'Br': 'Brassica rapa',
        'Gr': 'Gossypium raimondii',
        'Tsi': 'Tetracentron sinense',
        'Pb': 'Pyrus bretschneideri',
        'Lal': 'Lupinus albus',
        'Pt': 'Populus trichocarpa',
        'Tra': 'Triticum aestivum',
        'Me': 'Manihot esculenta',
        'Lan': 'Lupinus angustifolius',
        'Eg': 'Eucalyptus grandis',
        'Cca': 'Cajanus cajan',
        'Zm': 'Zea mays',
        'Mt': 'Medicago truncatula',
        'Qr': 'Quercus robur',
        'Pvu': 'Phaseolus vulgaris',
        'Dc': 'Daucus carota',
        'Cmi': 'Cucumis melo',
        'Cma': 'Cucurbita maxima',
        'Sl': 'Solanum lycopersicum',
        'Cmo': 'Cucumis melo',
        'Lj': 'Lotus japonicus',
        'Bx': 'Bambusoideae',
        'Ara': 'Arabis alpina',
        'Va': 'Vigna angularis',
        'Vv': 'Vitis vinifera',
        'W6Xd': 'Vigna unguiculata',
        'Lsa': 'Lactuca sativa',
        'Vr': 'Vigna radiata',
        'Rc': 'Ricinus communis',
        'W6Xa': 'Vigna unguiculata',
        'Aet': 'Aegilops tauschii',
        'Tc': 'Theobroma cacao',
        'Hv': 'Hordeum vulgare',
        'Sm': 'Solanum melongena',
        'Al': 'Arabidopsis lyrata',
        'Ps': 'Pisum sativum',
        'Nn': 'Nelumbo nucifera',
        'Can': 'Cannabis sativa',
        'Cr': 'Capsella rubella',
        'Tp': 'Trifolium pratense',
        'W6Xb': 'Vigna unguiculata',
        'Pp': 'Physcomitrella patens',
        'At': 'Arabidopsis thaliana',
        'Tdza': 'Triticum dicoccoides',
        'Tu': 'Triticum urartu',
        'Ata': 'Aegilops tauschii',
        'Tdzb': 'Triticum dicoccoides',
        'Pm': 'Prunus mume',
        'Ccl': 'Citrus clementina',
        'Cd': 'Citrus deliciosa',
        'Da': 'Daucus carota',
        'Sin': 'Sesamum indicum',
        'Ah': 'Arachis hypogaea',
        'Si': 'Setaria italica',
        'Bd': 'Brachypodium distachyon',
        'Ces': 'Camelina sativa',
        'Ot': 'Oropetium thomaeum',
        'Os': 'Oryza sativa',
        'Sb': 'Sorghum bicolor',
        'Tdsb': 'Triticum durum',
        'Fv': 'Fragaria vesca',
        'Lc': 'Lens culinaris',
        'Ac': 'Actinidia chinensis',
        # Add additional mappings for the short forms in the screenshot
        'Cl': 'Citrullus lanatus',
        'Coc': 'Cocos nucifera',
        'Cpa': 'Carica papaya',
        'Cpp': 'Cucurbita pepo',
        'Car': 'Coffea arabica',
        'Cs': 'Citrus sinensis',
        'Lsi': 'Linum usitatissimum',
        'Ao': 'Asparagus officinalis',
        'Nc': 'Noccaea caerulescens',
        'Cme': 'Cyanidioschyzon merolae',
        'Sp': 'Spirodela polyrhiza',
        'Amt': 'Amborella trichopoda',
        'Elg': 'Elaeis guineensis',
        'Tdsa': 'Triticum durum'
    }
    
    if clean_id in ui_abbreviations:
        return ui_abbreviations[clean_id]
    
    # If no match found, format the species_id to look like a species name
    formatted_name = species_id.replace('_', ' ').title()
    logger.warning(f"No mapping found for species ID: {species_id}, using formatted ID: {formatted_name}")
    return formatted_name