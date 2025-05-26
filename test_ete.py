# test_ete.py - Run this to test ETE3 installation
import sys

def test_ete_installation():
    print("🧪 Testing ETE3 installation...")
    
    try:
        # Test 1: Import ETE3
        print("1️⃣ Testing ETE3 import...")
        import ete3
        from ete3 import Tree, TreeStyle, NodeStyle
        print(f"   ✅ ETE3 version {ete3.__version__} imported successfully!")
        
        # Test 2: Create a simple tree
        print("2️⃣ Testing tree creation...")
        t = Tree("(A:1,(B:1,(C:1,D:1):0.5):0.5);")
        print(f"   ✅ Tree created: {t}")
        
        # Test 3: Test tree traversal
        print("3️⃣ Testing tree traversal...")
        leaves = t.get_leaves()
        print(f"   ✅ Found {len(leaves)} leaves: {[leaf.name for leaf in leaves]}")
        
        # Test 4: Test tree distance calculations
        print("4️⃣ Testing distance calculations...")
        for leaf in leaves:
            distance = leaf.get_distance(t)
            print(f"   📏 Distance from {leaf.name} to root: {distance}")
        
        # Test 5: Test imports needed for image generation
        print("5️⃣ Testing image generation imports...")
        import tempfile
        import base64
        print("   ✅ Image generation imports working!")
        
        print("\n🎉 All ETE3 tests passed! Ready for integration!")
        return True
        
    except ImportError as e:
        print(f"   ❌ Import failed: {e}")
        print(f"\n💡 To fix this, run:")
        print(f"   conda activate orthoviewer2")
        print(f"   conda install -c etetoolkit ete3")
        return False
        
    except Exception as e:
        print(f"   ❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ete_installation()
    sys.exit(0 if success else 1)