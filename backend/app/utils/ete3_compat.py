"""
ETE3 compatibility wrapper to handle missing TreeStyle in headless environments
"""

try:
    from ete3 import Tree, TreeStyle, NodeStyle, TextFace
    ETE3_GUI_AVAILABLE = True
except ImportError:
    try:
        from ete3 import Tree
        # Create dummy classes for headless operation
        class TreeStyle:
            def __init__(self):
                pass
        
        class NodeStyle:
            def __init__(self):
                pass
                
        class TextFace:
            def __init__(self, text):
                self.text = text
        
        ETE3_GUI_AVAILABLE = False
    except ImportError:
        raise ImportError("ETE3 is not properly installed")

def get_tree_with_style(newick_string):
    """Create a tree with style if GUI components are available"""
    tree = Tree(newick_string)
    
    if ETE3_GUI_AVAILABLE:
        ts = TreeStyle()
        ts.show_leaf_name = True
        return tree, ts
    else:
        return tree, None

def is_gui_available():
    """Check if ETE3 GUI components are available"""
    return ETE3_GUI_AVAILABLE
