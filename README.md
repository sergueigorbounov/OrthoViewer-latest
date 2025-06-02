# OrthoViewer

**A Comprehensive Platform for Biological Data Visualization and Phylogenetic Analysis**

OrthoViewer is a modern web-based platform designed for the visualization and analysis of biological data, with particular emphasis on orthogroups and phylogenetic relationships. The platform integrates contemporary web technologies with specialized bioinformatics tools to provide researchers with robust analytical capabilities for comparative genomics studies.

## Scientific Context

This platform addresses the growing need for interactive visualization tools in comparative genomics and phylogenetic analysis. OrthoViewer provides researchers with the capability to explore orthologous gene relationships across species, visualize phylogenetic trees, and perform comprehensive genomic data analysis through an intuitive web interface.

The increasing complexity of comparative genomics datasets necessitates sophisticated computational tools that can handle large-scale phylogenetic analyses while maintaining scientific rigor. OrthoViewer fills this gap by providing a robust, test-driven platform that ensures reproducible results in evolutionary biology research.

## Quick Start

### Prerequisites

Before installation, ensure you have the following requirements:

- **Python 3.10+** (conda/miniforge recommended for best package management)
- **Node.js 16+** with npm
- **Git** for version control

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd orthoviewer2
   ```

2. **Set up the conda environment (Recommended):**
   ```bash
   # Install conda/miniforge if not available:
   # https://github.com/conda-forge/miniforge
   
   # Create and activate the orthoviewer2 environment
   conda env create -f environment.yml
   conda activate orthoviewer2
   ```

3. **Alternative: Install with pip (if conda not available):**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

4. **Install frontend dependencies:**
   ```bash
   cd frontend-vite
   npm install
   cd ..
   ```

### Running the Application

**One-command startup:**
```bash
./dev.sh
```

This script will:
- Automatically create/activate the conda environment
- Start the FastAPI backend on http://localhost:8003
- Launch the Vite frontend on http://localhost:5173
- Set up hot-reload for development

**Manual startup (alternative):**
```bash
# Terminal 1 - Backend
conda activate orthoviewer2
cd backend
uvicorn app.fastapi_main:app --host 0.0.0.0 --port 8003 --reload

# Terminal 2 - Frontend
cd frontend-vite
npm run dev
```

### Access the Application

- **Frontend**: http://localhost:5173
- **API Documentation**: http://localhost:8003/docs
- **API Health Check**: http://localhost:8003/api/health

### Test-Driven Development

For development with continuous testing:
```bash
./tdd.sh
```

This provides a comprehensive TDD environment with automated test execution, code formatting, and development tools.

### Verification

Test that everything is working:
```bash
# Test backend packages
conda activate orthoviewer2
python -c "import fastapi, uvicorn, ete3, pytest, pandas, prometheus_client; print('✓ All packages imported successfully')"

# Test frontend build
cd frontend-vite
npm run build
```

### Troubleshooting

**Common Issues:**

- **Conda not found**: Install conda/miniforge from https://github.com/conda-forge/miniforge
- **Environment creation fails**: Make sure you have write permissions and sufficient disk space
- **Backend import errors**: Verify conda environment is activated: `conda activate orthoviewer2`
- **Frontend fails to start**: Ensure Node.js 16+ is installed and `npm install` completed successfully
- **Port conflicts**: The script automatically handles port conflicts, but you can manually kill processes using ports 8003/5173

**Getting Help:**
- Check logs in the `logs/` directory for detailed error messages
- Run `./dev.sh --help` for usage information
- Run `./tdd.sh --help` for development environment help

## Technical Architecture

### System Overview

OrthoViewer employs a modern microservices architecture orchestrated through containerization and designed for scalability in scientific computing environments:

```
┌─────────────────────────────────────────────────────────────────┐
│                    OrthoViewer Architecture                     │
├─────────────────────────────────────────────────────────────────┤
│  Presentation Layer                                             │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │   React Client  │    │   Nginx Proxy   │                   │
│  │   (TypeScript)  │◄──►│   Load Balancer │                   │
│  └─────────────────┘    └─────────────────┘                   │
├─────────────────────────────────────────────────────────────────┤
│  API Gateway Layer                                             │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │   FastAPI       │    │   WebSocket     │                   │
│  │   REST API      │    │   Real-time     │                   │
│  └─────────────────┘    └─────────────────┘                   │
├─────────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                          │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │ Phylogenetic    │    │ Orthogroup      │                   │
│  │ Services        │    │ Classification  │                   │
│  └─────────────────┘    └─────────────────┘                   │
├─────────────────────────────────────────────────────────────────┤
│  Data Processing Layer                                         │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │ ETE3 Toolkit    │    │ Data Validation │                   │
│  │ Integration     │    │ (Pydantic)      │                   │
│  └─────────────────┘    └─────────────────┘                   │
├─────────────────────────────────────────────────────────────────┤
│  Infrastructure Layer                                          │
│  ┌─────────────────┐    ┌─────────────────┐                   │
│  │ Docker          │    │ Test Framework  │                   │
│  │ Containers      │    │ (Pytest)       │                   │
│  └─────────────────┘    └─────────────────┘                   │
└─────────────────────────────────────────────────────────────────┘
```

### Core Technologies

**Backend Infrastructure**
- **Framework**: FastAPI (Python 3.10+) - High-performance, standards-based API framework
- **Phylogenetic Analysis**: ETE3 Toolkit - Comprehensive phylogenetic tree manipulation library
- **Data Processing**: Pandas, NumPy for biological data manipulation and analysis
- **Data Validation**: Pydantic models for type-safe orthogroup and species structures
- **Testing**: Pytest with comprehensive test-driven development methodology
- **API Documentation**: Automated OpenAPI/Swagger generation with interactive documentation
- **Asynchronous Runtime**: Uvicorn ASGI server with hot-reload and multi-worker support

**Frontend Implementation**
- **Framework**: React with TypeScript for type-safe component development
- **Build Systems**: Vite (recommended) and Webpack (legacy support) for optimized bundling
- **UI Components**: Material-UI (MUI) for consistent, accessible interface components
- **Data Visualization**: D3.js for interactive phylogenetic tree rendering and biological data graphics
- **State Management**: Redux Toolkit for predictable application state management
- **Testing**: Jest, React Testing Library, Cypress for comprehensive frontend testing

**Infrastructure & Deployment**
- **Containerization**: Docker and Docker Compose for reproducible deployment environments
- **Reverse Proxy**: Nginx for request routing, load balancing, and static file serving
- **Development Environment**: Hot-reload capabilities with integrated test-driven development
- **CI/CD**: GitHub Actions for automated testing, building, and deployment pipelines
- **Monitoring**: Prometheus and Grafana for system performance monitoring and alerting

## Test-Driven Development Methodology

### TDD Philosophy and Scientific Software Development

OrthoViewer employs a rigorous Test-Driven Development approach specifically adapted for scientific software development. This methodology ensures that all biological analyses are reproducible, verifiable, and maintain scientific integrity throughout the development lifecycle.

### Enhanced TDD Cycle for Biological Research

The traditional Red-Green-Refactor cycle is enhanced with domain-specific considerations for biological data analysis:

1. **Red Phase - Scientific Specification**
   - Define expected biological behavior through failing tests
   - Specify input/output requirements for phylogenetic analyses
   - Document edge cases specific to evolutionary biology data
   - Establish performance benchmarks for computational biology operations
   - Define statistical significance thresholds for analytical outputs

2. **Green Phase - Minimal Implementation**
   - Implement minimal code to satisfy biological requirements
   - Focus on scientific accuracy over premature optimization
   - Ensure compliance with established bioinformatics standards
   - Validate against known biological datasets and benchmarks
   - Implement proper error handling for malformed biological data

3. **Refactor Phase - Optimization and Enhancement**
   - Enhance performance while maintaining scientific correctness
   - Improve code readability for collaborative research environments
   - Optimize memory usage for large phylogenetic datasets
   - Enhance error handling and user feedback mechanisms
   - Document assumptions, limitations, and algorithmic choices

4. **Validation Phase - Scientific Verification**
   - Cross-validate results against established phylogenetic analysis tools
   - Verify statistical significance and confidence intervals
   - Ensure reproducibility across different computational environments
   - Benchmark performance against industry-standard tools
   - Document validation procedures and results

### TDD Environment Architecture

The TDD environment provides a comprehensive development ecosystem optimized for biological software development:

```bash
# Complete TDD Environment Initialization
./tdd.sh
```

**Environment Orchestration Process:**

1. **System Validation and Prerequisites**
   - Verify Python 3.10+ installation and development headers
   - Check Node.js 16+ and npm availability for frontend development
   - Validate Git configuration and repository access
   - Ensure adequate system resources (memory, disk space, network)

2. **Python Environment Management**
   - Create isolated Conda environment with reproducible dependency versions
   - Install backend dependencies with precise version pinning
   - Configure Python path for modular development and testing
   - Set up development tools (Black, Flake8, MyPy, pre-commit hooks)

3. **Service Orchestration and Management**
   - Launch FastAPI backend with development configuration
   - Start frontend development server with hot-reload capabilities
   - Initialize database connections and data migration procedures
   - Configure reverse proxy for unified development environment

4. **Test Infrastructure Initialization**
   - Configure Pytest with scientific computing optimizations
   - Set up continuous test execution with file system monitoring
   - Initialize coverage analysis with configurable thresholds
   - Configure performance benchmarking for computational biology operations

5. **Development Tools Integration**
   - Initialize code formatting and linting with scientific code standards
   - Set up type checking with biological data model validation
   - Configure documentation generation from code annotations
   - Enable debugging support with scientific data inspection capabilities

### Comprehensive Testing Framework

**Unit Testing Architecture**

Unit tests focus on individual components of biological analysis pipelines with scientific rigor:

```python
# Phylogenetic Analysis Unit Tests
import pytest
from hypothesis import given, strategies as st
from app.services.phylogenetic import PhylogeneticAnalyzer
from app.models.phylo import NewickTree, PhylogeneticNode

class TestNewickTreeParsing:
    """Comprehensive unit tests for Newick tree parsing functionality."""
    
    def test_basic_newick_parsing(self):
        """Test parsing of standard Newick format trees."""
        newick_string = "((A:0.1,B:0.2):0.05,C:0.3);"
        tree = NewickTree.parse(newick_string)
        
        assert tree.get_topology_only() == "((A,B),C);"
        assert len(tree.get_leaves()) == 3
        assert tree.get_distance("A", "B") == 0.3
        assert tree.get_common_ancestor(["A", "B"]).name == ""
    
    def test_complex_newick_with_support_values(self):
        """Test parsing of Newick trees with bootstrap support values."""
        newick_with_support = "((A:0.1,B:0.2)0.95:0.05,C:0.3)0.99;"
        tree = NewickTree.parse(newick_with_support)
        
        assert tree.root.support == 0.99
        internal_node = tree.get_common_ancestor(["A", "B"])
        assert internal_node.support == 0.95
    
    @given(st.integers(min_value=3, max_value=100))
    def test_random_tree_generation_properties(self, species_count):
        """Property-based testing for random tree generation."""
        tree = NewickTree.generate_random(species_count)
        
        assert len(tree.get_leaves()) == species_count
        assert tree.is_binary()
        assert tree.check_monophyly(tree.get_leaf_names())[0]
        assert all(node.dist >= 0 for node in tree.traverse())

class TestOrthogroupClassification:
    """Unit tests for orthogroup classification algorithms."""
    
    def test_basic_orthogroup_assignment(self):
        """Test basic orthogroup classification functionality."""
        gene_data = {
            "species_A": ["gene1", "gene2", "gene3"],
            "species_B": ["gene4", "gene5", "gene6"],
            "species_C": ["gene7", "gene8", "gene9"]
        }
        
        classifier = OrthogroupClassifier()
        orthogroups = classifier.classify(gene_data)
        
        assert len(orthogroups) > 0
        assert all(og.species_count >= 2 for og in orthogroups)
        assert sum(len(og.genes) for og in orthogroups) == 9
    
    def test_single_copy_orthogroup_detection(self):
        """Test detection of single-copy orthogroups."""
        single_copy_data = {
            "species_A": ["scog1"],
            "species_B": ["scog1_ortholog"],
            "species_C": ["scog1_ortholog"]
        }
        
        classifier = OrthogroupClassifier()
        orthogroups = classifier.classify(single_copy_data)
        
        single_copy_groups = [og for og in orthogroups if og.is_single_copy()]
        assert len(single_copy_groups) >= 1
        assert all(og.species_count == 3 for og in single_copy_groups)

class TestPhylogeneticStatistics:
    """Unit tests for phylogenetic statistical analysis."""
    
    def test_tree_balance_calculation(self):
        """Test calculation of tree balance indices."""
        balanced_tree = NewickTree.parse("((A,B),(C,D));")
        imbalanced_tree = NewickTree.parse("(((A,B),C),D);")
        
        analyzer = PhylogeneticAnalyzer()
        
        balanced_index = analyzer.calculate_balance_index(balanced_tree)
        imbalanced_index = analyzer.calculate_balance_index(imbalanced_tree)
        
        assert balanced_index > imbalanced_index
        assert 0 <= balanced_index <= 1
        assert 0 <= imbalanced_index <= 1
    
    def test_evolutionary_distance_matrix(self):
        """Test calculation of evolutionary distance matrices."""
        tree = NewickTree.parse("((A:0.1,B:0.2):0.05,(C:0.15,D:0.25):0.1);")
        analyzer = PhylogeneticAnalyzer()
        
        distance_matrix = analyzer.calculate_distance_matrix(tree)
        
        assert distance_matrix.shape == (4, 4)
        assert np.allclose(distance_matrix, distance_matrix.T)  # Symmetric
        assert np.all(np.diag(distance_matrix) == 0)  # Zero diagonal
        assert np.all(distance_matrix >= 0)  # Non-negative distances
```

**Integration Testing Framework**

Integration tests verify correct interaction between system components with real biological data:

```python
# API Integration Tests
import pytest
from fastapi.testclient import TestClient
from app.fastapi_main import app
from app.models.phylo import PhylogeneticAnalysisRequest

class TestPhylogeneticAPI:
    """Integration tests for phylogenetic analysis API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client for API testing."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_newick_data(self):
        """Provide sample Newick tree data for testing."""
        return {
            "newick_tree": "((Homo_sapiens:0.1,Pan_troglodytes:0.12):0.05,(Mus_musculus:0.8,Rattus_norvegicus:0.85):0.3);",
            "analysis_options": {
                "calculate_statistics": True,
                "include_support_values": False,
                "root_method": "midpoint"
            }
        }
    
    def test_phylogenetic_tree_upload_and_analysis(self, client, sample_newick_data):
        """Test complete phylogenetic tree analysis workflow."""
        response = client.post("/api/phylo/analyze", json=sample_newick_data)
        
        assert response.status_code == 200
        result = response.json()
        
        # Verify response structure
        assert "tree_id" in result
        assert "statistics" in result
        assert "processed_tree" in result
        
        # Verify biological accuracy
        stats = result["statistics"]
        assert stats["leaf_count"] == 4
        assert stats["internal_node_count"] == 3
        assert stats["is_rooted"] is True
        assert stats["is_binary"] is True
    
    def test_orthogroup_analysis_endpoint(self, client):
        """Test orthogroup classification API endpoint."""
        orthogroup_data = {
            "species_data": {
                "Arabidopsis_thaliana": ["AT1G01010", "AT1G01020", "AT1G01030"],
                "Oryza_sativa": ["LOC_Os01g01010", "LOC_Os01g01020", "LOC_Os01g01030"],
                "Zea_mays": ["GRMZM2G000001", "GRMZM2G000002", "GRMZM2G000003"]
            },
            "classification_method": "reciprocal_best_hits",
            "e_value_threshold": 1e-5
        }
        
        response = client.post("/api/orthogroups/classify", json=orthogroup_data)
        
        assert response.status_code == 200
        result = response.json()
        
        assert "orthogroups" in result
        assert "classification_summary" in result
        assert len(result["orthogroups"]) > 0
    
    def test_data_validation_and_error_handling(self, client):
        """Test API validation and error handling with malformed data."""
        invalid_newick = {
            "newick_tree": "invalid_newick_format((A,B);",
            "analysis_options": {}
        }
        
        response = client.post("/api/phylo/analyze", json=invalid_newick)
        
        assert response.status_code == 422  # Validation error
        error_details = response.json()
        assert "detail" in error_details
        assert "newick_tree" in str(error_details["detail"])

class TestDatabaseIntegration:
    """Integration tests for database operations."""
    
    @pytest.fixture
    def test_database(self):
        """Set up test database with sample data."""
        # Database setup logic here
        pass
    
    def test_phylogenetic_tree_storage_and_retrieval(self, test_database):
        """Test storing and retrieving phylogenetic trees from database."""
        tree_data = {
            "newick_string": "((A,B),(C,D));",
            "metadata": {"source": "test", "date_created": "2025-01-01"}
        }
        
        # Store tree
        tree_id = store_phylogenetic_tree(tree_data)
        assert tree_id is not None
        
        # Retrieve tree
        retrieved_tree = get_phylogenetic_tree(tree_id)
        assert retrieved_tree["newick_string"] == tree_data["newick_string"]
        assert retrieved_tree["metadata"]["source"] == "test"
    
    def test_orthogroup_data_persistence(self, test_database):
        """Test persistence of orthogroup classification results."""
        orthogroup_result = {
            "orthogroup_id": "OG0000001",
            "species_genes": {
                "species_A": ["gene1", "gene2"],
                "species_B": ["gene3", "gene4"]
            },
            "classification_method": "reciprocal_best_hits"
        }
        
        # Store orthogroup
        stored_id = store_orthogroup(orthogroup_result)
        assert stored_id == "OG0000001"
        
        # Retrieve orthogroup
        retrieved_og = get_orthogroup("OG0000001")
        assert retrieved_og["species_genes"] == orthogroup_result["species_genes"]
```

**Performance and Load Testing Framework**

Performance tests ensure computational efficiency for large-scale biological datasets:

```python
# Performance Testing Suite
import pytest
import time
import psutil
import numpy as np
from app.services.phylogenetic import LargeScalePhylogeneticAnalyzer

class TestPerformanceBenchmarks:
    """Performance benchmarks for phylogenetic analysis operations."""
    
    @pytest.mark.performance
    def test_large_tree_processing_performance(self):
        """Benchmark processing of large phylogenetic trees."""
        # Generate large test tree with 1000 species
        large_tree = generate_random_tree(species_count=1000)
        analyzer = LargeScalePhylogeneticAnalyzer()
        
        # Measure processing time and memory usage
        process = psutil.Process()
        memory_before = process.memory_info().rss
        start_time = time.time()
        
        result = analyzer.analyze_tree_structure(large_tree)
        
        end_time = time.time()
        memory_after = process.memory_info().rss
        
        execution_time = end_time - start_time
        memory_usage = memory_after - memory_before
        
        # Performance assertions
        assert execution_time < 5.0  # Maximum 5 seconds
        assert memory_usage < 200 * 1024 * 1024  # Maximum 200MB
        assert result.accuracy >= 0.98  # Minimum 98% accuracy
        
        # Log performance metrics
        pytest.performance_metrics = {
            "execution_time": execution_time,
            "memory_usage": memory_usage,
            "accuracy": result.accuracy
        }
    
    @pytest.mark.performance
    def test_concurrent_analysis_performance(self):
        """Test performance under concurrent analysis requests."""
        import concurrent.futures
        
        def analyze_tree(tree_data):
            analyzer = PhylogeneticAnalyzer()
            return analyzer.analyze(tree_data)
        
        # Generate multiple test trees
        test_trees = [generate_random_tree(50) for _ in range(10)]
        
        start_time = time.time()
        
        # Execute concurrent analyses
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(analyze_tree, tree) for tree in test_trees]
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Verify all analyses completed successfully
        assert len(results) == 10
        assert all(result.is_valid() for result in results)
        assert total_time < 10.0  # Maximum 10 seconds for all analyses
    
    @pytest.mark.performance
    def test_memory_efficiency_large_datasets(self):
        """Test memory efficiency with large biological datasets."""
        # Simulate large orthogroup dataset
        large_dataset = generate_large_orthogroup_dataset(
            species_count=100,
            genes_per_species=10000
        )
        
        classifier = MemoryEfficientOrthogroupClassifier()
        
        # Monitor memory usage during classification
        memory_tracker = MemoryUsageTracker()
        memory_tracker.start()
        
        result = classifier.classify_large_dataset(large_dataset)
        
        memory_stats = memory_tracker.stop()
        
        # Memory efficiency assertions
        assert memory_stats.peak_usage < 1024 * 1024 * 1024  # Maximum 1GB
        assert memory_stats.memory_leaks == 0
        assert len(result.orthogroups) > 0

@pytest.mark.load_testing
class TestLoadTesting:
    """Load testing for API endpoints under high concurrency."""
    
    def test_api_load_capacity(self):
        """Test API performance under high load conditions."""
        import asyncio
        import aiohttp
        
        async def make_request(session, url, data):
            async with session.post(url, json=data) as response:
                return await response.json()
        
        async def load_test():
            url = "http://localhost:8002/api/phylo/analyze"
            test_data = {"newick_tree": "((A,B),(C,D));"}
            
            async with aiohttp.ClientSession() as session:
                tasks = [make_request(session, url, test_data) for _ in range(100)]
                results = await asyncio.gather(*tasks)
                return results
        
        start_time = time.time()
        results = asyncio.run(load_test())
        end_time = time.time()
        
        # Load testing assertions
        assert len(results) == 100
        assert all("tree_id" in result for result in results)
        assert (end_time - start_time) < 30.0  # Maximum 30 seconds for 100 requests
```

**End-to-End Testing Framework**

Comprehensive end-to-end tests validate complete user workflows:

```python
# End-to-End Testing Suite using Playwright
import pytest
from playwright.sync_api import sync_playwright, Page, BrowserContext

class TestEndToEndWorkflows:
    """End-to-end tests for complete user workflows."""
    
    @pytest.fixture(scope="session")
    def browser_context(self):
        """Set up browser context for E2E testing."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="OrthoViewer E2E Test Suite"
            )
            yield context
            browser.close()
    
    @pytest.fixture
    def page(self, browser_context: BrowserContext):
        """Create new page for each test."""
        page = browser_context.new_page()
        yield page
        page.close()
    
    def test_complete_phylogenetic_analysis_workflow(self, page: Page):
        """Test complete workflow from data upload to result visualization."""
        # Navigate to application
        page.goto("http://localhost:3000")
        
        # Verify page load
        page.wait_for_selector("[data-testid='app-header']")
        assert page.title() == "OrthoViewer - Phylogenetic Analysis Platform"
        
        # Navigate to analysis page
        page.click("[data-testid='nav-analysis']")
        page.wait_for_selector("[data-testid='analysis-form']")
        
        # Upload phylogenetic tree data
        page.fill("[data-testid='newick-input']", "((Human,Chimp),(Mouse,Rat));")
        page.click("[data-testid='analyze-button']")
        
        # Wait for analysis completion
        page.wait_for_selector("[data-testid='analysis-results']", timeout=10000)
        
        # Verify results display
        assert page.is_visible("[data-testid='tree-visualization']")
        assert page.is_visible("[data-testid='statistics-panel']")
        
        # Verify tree statistics
        leaf_count = page.inner_text("[data-testid='leaf-count']")
        assert leaf_count == "4"
        
        # Test tree interaction
        page.click("[data-testid='tree-node-Human']")
        assert page.is_visible("[data-testid='node-details-panel']")
        
        # Test export functionality
        page.click("[data-testid='export-button']")
        page.wait_for_selector("[data-testid='export-options']")
        
        with page.expect_download() as download_info:
            page.click("[data-testid='export-svg']")
        download = download_info.value
        assert download.suggested_filename.endswith('.svg')
    
    def test_orthogroup_classification_workflow(self, page: Page):
        """Test complete orthogroup classification workflow."""
        # Navigate to orthogroup analysis
        page.goto("http://localhost:3000/orthogroups")
        
        # Upload species gene data
        species_data = {
            "Arabidopsis": ["AT1G01010", "AT1G01020"],
            "Rice": ["LOC_Os01g01010", "LOC_Os01g01020"]
        }
        
        # Fill in species data forms
        for species, genes in species_data.items():
            page.fill(f"[data-testid='species-{species}-input']", "\n".join(genes))
        
        # Configure classification parameters
        page.select_option("[data-testid='method-select']", "reciprocal_best_hits")
        page.fill("[data-testid='evalue-input']", "1e-5")
        
        # Start classification
        page.click("[data-testid='classify-button']")
        
        # Wait for results
        page.wait_for_selector("[data-testid='orthogroup-results']", timeout=30000)
        
        # Verify orthogroup display
        assert page.is_visible("[data-testid='orthogroup-table']")
        
        # Test orthogroup interaction
        page.click("[data-testid='orthogroup-OG0000001']")
        assert page.is_visible("[data-testid='orthogroup-details']")
        
        # Verify gene assignments
        genes_display = page.inner_text("[data-testid='assigned-genes']")
        assert "AT1G01010" in genes_display
        assert "LOC_Os01g01010" in genes_display
    
    def test_data_visualization_interactions(self, page: Page):
        """Test interactive data visualization features."""
        # Load pre-existing analysis
        page.goto("http://localhost:3000/analysis/sample-tree")
        page.wait_for_selector("[data-testid='tree-visualization']")
        
        # Test zoom functionality
        page.click("[data-testid='zoom-in-button']")
        # Verify zoom level increased
        zoom_level = page.get_attribute("[data-testid='svg-container']", "data-zoom")
        assert float(zoom_level) > 1.0
        
        # Test node selection and highlighting
        page.click("[data-testid='tree-node-species1']")
        assert page.has_class("[data-testid='tree-node-species1']", "selected")
        
        # Test branch length display toggle
        page.click("[data-testid='show-branch-lengths']")
        assert page.is_visible("[data-testid='branch-length-0.1']")
        
        # Test tree rooting functionality
        page.click("[data-testid='reroot-button']")
        page.click("[data-testid='tree-node-outgroup']")
        page.wait_for_selector("[data-testid='rerooted-tree']")
        
        # Verify tree structure changed
        root_position = page.get_attribute("[data-testid='tree-root']", "data-position")
        assert root_position != "default"
    
    def test_cross_browser_compatibility(self):
        """Test application functionality across different browsers."""
        browsers = ['chromium', 'firefox', 'webkit']
        
        for browser_name in browsers:
            with sync_playwright() as p:
                browser = getattr(p, browser_name).launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                # Basic functionality test
                page.goto("http://localhost:3000")
                page.wait_for_selector("[data-testid='app-header']")
                
                # Test core feature
                page.fill("[data-testid='newick-input']", "((A,B),(C,D));")
                page.click("[data-testid='analyze-button']")
                page.wait_for_selector("[data-testid='analysis-results']")
                
                # Verify results
                assert page.is_visible("[data-testid='tree-visualization']")
                
                browser.close()
    
    def test_responsive_design_mobile(self, browser_context: BrowserContext):
        """Test responsive design on mobile devices."""
        # Set mobile viewport
        mobile_context = browser_context.new_context(
            viewport={"width": 375, "height": 667},
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
        )
        
        page = mobile_context.new_page()
        page.goto("http://localhost:3000")
        
        # Verify mobile navigation
        assert page.is_visible("[data-testid='mobile-menu-button']")
        page.click("[data-testid='mobile-menu-button']")
        assert page.is_visible("[data-testid='mobile-navigation']")
        
        # Test mobile-optimized tree visualization
        page.goto("http://localhost:3000/analysis/sample-tree")
        assert page.is_visible("[data-testid='mobile-tree-viewer']")
        
        # Test touch interactions
        page.tap("[data-testid='tree-node-species1']")
        assert page.is_visible("[data-testid='mobile-node-details']")
        
        mobile_context.close()

@pytest.mark.accessibility
class TestAccessibilityCompliance:
    """Accessibility testing for WCAG compliance."""
    
    def test_keyboard_navigation(self, page: Page):
        """Test complete keyboard navigation functionality."""
        page.goto("http://localhost:3000")
        
        # Test tab navigation
        page.keyboard.press("Tab")
        focused_element = page.evaluate("document.activeElement.getAttribute('data-testid')")
        assert focused_element == "nav-analysis"
        
        # Test enter key activation
        page.keyboard.press("Enter")
        page.wait_for_selector("[data-testid='analysis-form']")
        
        # Test form navigation
        page.keyboard.press("Tab")
        page.type("((A,B),(C,D));")
        page.keyboard.press("Tab")
        page.keyboard.press("Enter")
        
        # Verify analysis started
        page.wait_for_selector("[data-testid='analysis-results']")
    
    def test_screen_reader_compatibility(self, page: Page):
        """Test screen reader accessibility features."""
        page.goto("http://localhost:3000")
        
        # Verify ARIA labels
        assert page.get_attribute("[data-testid='newick-input']", "aria-label") is not None
        assert page.get_attribute("[data-testid='analyze-button']", "aria-describedby") is not None
        
        # Verify semantic HTML structure
        assert page.query_selector("main") is not None
        assert page.query_selector("nav") is not None
        assert len(page.query_selector_all("h1, h2, h3")) > 0
    
    def test_color_contrast_compliance(self, page: Page):
        """Test color contrast ratios for WCAG AA compliance."""
        page.goto("http://localhost:3000")
        
        # Check contrast ratios programmatically
        contrast_results = page.evaluate("""
            () => {
                // Color contrast checking logic
                const elements = document.querySelectorAll('[data-testid]');
                const results = [];
                
                elements.forEach(el => {
                    const styles = window.getComputedStyle(el);
                    const color = styles.color;
                    const backgroundColor = styles.backgroundColor;
                    
                    // Calculate contrast ratio (simplified)
                    const contrast = calculateContrastRatio(color, backgroundColor);
                    results.push({
                        element: el.getAttribute('data-testid'),
                        contrast: contrast,
                        passes: contrast >= 4.5  // WCAG AA standard
                    });
                });
                
                return results;
            }
        """)
        
        # Verify all elements pass contrast requirements
        failing_elements = [r for r in contrast_results if not r['passes']]
        assert len(failing_elements) == 0, f"Contrast failures: {failing_elements}"
```

**Property-Based Testing with Hypothesis**

Advanced property-based testing for biological data validation:

```python
# Property-Based Testing Suite
from hypothesis import given, strategies as st, assume
from hypothesis.extra.numpy import arrays
import numpy as np

class TestBiologicalDataProperties:
    """Property-based tests for biological data structures and algorithms."""
    
    @given(st.integers(min_value=3, max_value=1000))
    def test_phylogenetic_tree_properties(self, num_species):
        """Test properties that should hold for all phylogenetic trees."""
        tree = generate_random_phylogenetic_tree(num_species)
        
        # Fundamental tree properties
        assert len(tree.get_leaves()) == num_species
        assert tree.is_binary() or tree.is_polytomy()
        assert tree.get_tree_root() is not None
        
        # Evolutionary distance properties
        distances = tree.get_distance_matrix()
        assert distances.shape == (num_species, num_species)
        assert np.allclose(distances, distances.T)  # Symmetric
        assert np.all(np.diag(distances) == 0)      # Zero diagonal
        assert np.all(distances >= 0)               # Non-negative
        
        # Tree topology properties
        assert tree.check_monophyly(tree.get_leaf_names())[0]
        assert len(tree.get_topology_only()) > 0
    
    @given(
        species_count=st.integers(min_value=2, max_value=50),
        genes_per_species=st.integers(min_value=10, max_value=1000)
    )
    def test_orthogroup_classification_properties(self, species_count, genes_per_species):
        """Test properties of orthogroup classification algorithms."""
        # Generate synthetic gene data
        gene_data = generate_synthetic_gene_data(species_count, genes_per_species)
        
        classifier = OrthogroupClassifier()
        orthogroups = classifier.classify(gene_data)
        
        # Classification properties
        total_input_genes = sum(len(genes) for genes in gene_data.values())
        total_classified_genes = sum(len(og.genes) for og in orthogroups)
        
        # Every gene should be classified exactly once
        assert total_classified_genes == total_input_genes
        
        # No orthogroup should be empty
        assert all(len(og.genes) > 0 for og in orthogroups)
        
        # Multi-species orthogroups should have genes from multiple species
        multi_species_ogs = [og for og in orthogroups if og.species_count > 1]
        assert all(og.species_count >= 2 for og in multi_species_ogs)
    
    @given(
        sequences=st.lists(
            st.text(alphabet="ATCG", min_size=50, max_size=5000),
            min_size=2,
            max_size=100
        )
    )
    def test_sequence_analysis_properties(self, sequences):
        """Test properties of biological sequence analysis."""
        assume(all(len(seq) > 0 for seq in sequences))
        
        analyzer = SequenceAnalyzer()
        
        for sequence in sequences:
            result = analyzer.analyze_sequence(sequence)
            
            # Basic sequence properties
            assert result.length == len(sequence)
            assert 0 <= result.gc_content <= 1
            assert result.nucleotide_composition['A'] >= 0
            assert result.nucleotide_composition['T'] >= 0
            assert result.nucleotide_composition['C'] >= 0
            assert result.nucleotide_composition['G'] >= 0
            
            # Conservation of nucleotides
            total_nucleotides = sum(result.nucleotide_composition.values())
            assert total_nucleotides == len(sequence)
            
            # GC content calculation verification
            gc_count = result.nucleotide_composition['G'] + result.nucleotide_composition['C']
            expected_gc = gc_count / len(sequence)
            assert abs(result.gc_content - expected_gc) < 1e-10
    
    @given(
        tree_newick=st.text(
            alphabet="(),;:0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz_.",
            min_size=10,
            max_size=1000
        )
    )
    def test_newick_parser_robustness(self, tree_newick):
        """Test Newick parser robustness with arbitrary input strings."""
        try:
            tree = NewickParser.parse(tree_newick)
            
            if tree is not None:  # Valid Newick format
                # If parsing succeeds, verify tree properties
                assert len(tree.get_leaves()) > 0
                assert tree.get_tree_root() is not None
                
                # Verify tree can be converted back to Newick
                reconstructed = tree.to_newick()
                reparsed = NewickParser.parse(reconstructed)
                assert reparsed is not None
        
        except InvalidNewickFormatError:
            # Invalid format is acceptable - parser should fail gracefully
            pass
        except Exception as e:
            # Unexpected exceptions should not occur
            pytest.fail(f"Unexpected exception: {e}")
    
    @given(
        distance_matrix=arrays(
            dtype=np.float64,
            shape=st.tuples(
                st.integers(min_value=3, max_value=20),
                st.integers(min_value=3, max_value=20)
            ).filter(lambda x: x[0] == x[1]),  # Square matrices only
            elements=st.floats(min_value=0.0, max_value=10.0, allow_nan=False)
        )
    )
    def test_distance_matrix_tree_construction(self, distance_matrix):
        """Test tree construction from distance matrices."""
        # Ensure matrix is symmetric and has zero diagonal
        n = distance_matrix.shape[0]
        distance_matrix = (distance_matrix + distance_matrix.T) / 2
        np.fill_diagonal(distance_matrix, 0)
        
        tree_builder = DistanceTreeBuilder()
        
        try:
            tree = tree_builder.build_tree(distance_matrix)
            
            # Verify constructed tree properties
            assert len(tree.get_leaves()) == n
            assert tree.is_binary()
            
            # Verify distance preservation (within tolerance)
            reconstructed_distances = tree.get_distance_matrix()
            correlation = np.corrcoef(
                distance_matrix.flatten(),
                reconstructed_distances.flatten()
            )[0, 1]
            assert correlation > 0.8  # Strong correlation expected
            
        except (InvalidDistanceMatrixError, TreeConstructionError):
            # Some distance matrices may not be suitable for tree construction
            pass
```

## Project Structure and Organization

### Comprehensive Directory Architecture

```
orthoviewer2-clean/
├── README.md                          # Comprehensive project documentation
├── LICENSE                           # GNU General Public License v3.0
├── CHANGELOG.md                      # Version history and release notes
├── CONTRIBUTING.md                   # Contribution guidelines and workflow
├── CODE_OF_CONDUCT.md               # Community guidelines and standards
├── SECURITY.md                      # Security policy and vulnerability reporting
├── .gitignore                       # Git ignore patterns for all environments
├── .pre-commit-config.yaml          # Pre-commit hooks configuration
├── pyproject.toml                   # Modern Python project configuration
├── setup.py                         # Package installation configuration
├── setup.cfg                        # Setup configuration and metadata
├── requirements.txt                 # Production Python dependencies
├── requirements-dev.txt             # Development Python dependencies
├── requirements-test.txt            # Testing-specific dependencies
├── tdd.sh                          # Test-driven development orchestration script
├── docker-compose.yml              # Production container orchestration
├── docker-compose.dev.yml          # Development container configuration
├── docker-compose.test.yml         # Testing environment configuration
├── Dockerfile                      # Multi-stage container build configuration
├── Dockerfile.dev                  # Development-optimized container configuration
├── .dockerignore                   # Docker build context exclusions
├── Makefile                        # Build automation and common tasks
├── justfile                        # Modern command runner alternative
│
├── backend/                        # Core application backend
│   ├── __init__.py                 # Backend package initialization
│   ├── app/                        # Application source code
│   │   ├── __init__.py             # Application package initialization
│   │   ├── main.py                 # FastAPI application entry point (legacy)
│   │   ├── fastapi_main.py         # FastAPI application entry point (current)
│   │   ├── asgi.py                 # ASGI application configuration
│   │   ├── wsgi.py                 # WSGI application configuration (if needed)
│   │   ├── config.py               # Application configuration management
│   │   ├── constants.py            # Application-wide constants
│   │   ├── exceptions.py           # Custom exception definitions
│   │   │
│   │   ├── api/                    # API layer implementation
│   │   │   ├── __init__.py         # API package initialization
│   │   │   ├── dependencies.py     # Shared API dependencies and injection
│   │   │   ├── middleware.py       # Custom middleware implementations
│   │   │   ├── security.py         # Authentication and authorization
│   │   │   ├── rate_limiting.py    # API rate limiting implementations
│   │   │   ├── v1/                 # API version 1 (current)
│   │   │   │   ├── __init__.py     # API v1 package initialization
│   │   │   │   ├── router.py       # Main API v1 router
│   │   │   │   ├── phylo.py        # Phylogenetic analysis endpoints
│   │   │   │   ├── orthogroups.py  # Orthogroup classification endpoints
│   │   │   │   ├── species.py      # Species management endpoints
│   │   │   │   ├── genes.py        # Gene annotation endpoints
│   │   │   │   ├── upload.py       # Data upload endpoints
│   │   │   │   ├── visualization.py # Data visualization endpoints
│   │   │   │   ├── export.py       # Data export endpoints
│   │   │   │   ├── search.py       # Search and query endpoints
│   │   │   │   ├── user.py         # User management endpoints
│   │   │   │   ├── project.py      # Project management endpoints
│   │   │   │   └── admin.py        # Administrative endpoints
│   │   │   └── v2/                 # API version 2 (planned)
│   │   │       ├── __init__.py     # API v2 package initialization
│   │   │       └── router.py       # Enhanced API v2 router
│   │   │
│   │   ├── models/                 # Data model definitions
│   │   │   ├── __init__.py         # Models package initialization
│   │   │   ├── base.py            # Base model classes and mixins
│   │   │   ├── enums.py           # Enumeration definitions
│   │   │   ├── phylo.py           # Phylogenetic data structures
│   │   │   ├── orthogroup.py      # Orthogroup classification models
│   │   │   ├── species.py         # Species taxonomy models
│   │   │   ├── gene.py            # Gene annotation models
│   │   │   ├── sequence.py        # Biological sequence models
│   │   │   ├── tree.py            # Tree structure models
│   │   │   ├── analysis.py        # Analysis result models
│   │   │   ├── user.py            # User account models
│   │   │   ├── project.py         # Project management models
│   │   │   ├── upload.py          # File upload models
│   │   │   └── export.py          # Data export models
│   │   │
│   │   ├── schemas/                # Pydantic schema definitions
│   │   │   ├── __init__.py         # Schemas package initialization
│   │   │   ├── base.py            # Base schema classes
│   │   │   ├── request.py         # API request schemas
│   │   │   ├── response.py        # API response schemas
│   │   │   ├── phylo.py           # Phylogenetic analysis schemas
│   │   │   ├── orthogroup.py      # Orthogroup schemas
│   │   │   ├── species.py         # Species schemas
│   │   │   ├── gene.py            # Gene schemas
│   │   │   ├── user.py            # User schemas
│   │   │   └── project.py         # Project schemas
│   │   │
│   │   ├── services/               # Business logic implementation
│   │   │   ├── __init__.py         # Services package initialization
│   │   │   ├── base.py            # Base service classes
│   │   │   ├── phylogenetic.py    # Phylogenetic analysis services
│   │   │   │   ├── tree_parser.py  # Tree parsing implementations
│   │   │   │   ├── tree_analysis.py # Tree analysis algorithms
│   │   │   │   ├── distance_calc.py # Distance calculation methods
│   │   │   │   └── reconstruction.py # Tree reconstruction methods
│   │   │   ├── orthogroup.py      # Orthogroup classification services
│   │   │   │   ├── classifier.py   # Classification algorithms
│   │   │   │   ├── validator.py    # Classification validation
│   │   │   │   └── statistics.py   # Orthogroup statistics
│   │   │   ├── sequence.py        # Sequence analysis services
│   │   │   │   ├── alignment.py    # Sequence alignment methods
│   │   │   │   ├── similarity.py   # Similarity calculations
│   │   │   │   └── annotation.py   # Sequence annotation
│   │   │   ├── data_processing.py # Data manipulation services
│   │   │   │   ├── parsers.py      # File format parsers
│   │   │   │   ├── converters.py   # Data format converters
│   │   │   │   ├── validators.py   # Data validation services
│   │   │   │   └── transformers.py # Data transformation utilities
│   │   │   ├── visualization.py   # Data visualization services
│   │   │   │   ├── tree_renderer.py # Tree visualization
│   │   │   │   ├── plot_generator.py # Statistical plots
│   │   │   │   └── export_formats.py # Export format handlers
│   │   │   ├── search.py          # Search and indexing services
│   │   │   ├── user.py            # User management services
│   │   │   ├── project.py         # Project management services
│   │   │   ├── cache.py           # Caching services
│   │   │   ├── notification.py    # Notification services
│   │   │   └── background_tasks.py # Background task processing
│   │   │
│   │   ├── repositories/           # Data access layer
│   │   │   ├── __init__.py         # Repositories package initialization
│   │   │   ├── base.py            # Base repository classes
│   │   │   ├── phylo.py           # Phylogenetic data repository
│   │   │   ├── orthogroup.py      # Orthogroup data repository
│   │   │   ├── species.py         # Species data repository
│   │   │   ├── gene.py            # Gene data repository
│   │   │   ├── user.py            # User data repository
│   │   │   ├── project.py         # Project data repository
│   │   │   ├── cache.py           # Cache repository
│   │   │   └── file_storage.py    # File storage repository
│   │   │
│   │   ├── database/               # Database configuration and management
│   │   │   ├── __init__.py         # Database package initialization
│   │   │   ├── connection.py      # Database connection management
│   │   │   ├── session.py         # Database session management
│   │   │   ├── migrations/        # Database migration scripts
│   │   │   │   ├── __init__.py     # Migrations package initialization
│   │   │   │   ├── env.py          # Alembic environment configuration
│   │   │   │   ├── script.py.mako  # Migration script template
│   │   │   │   └── versions/       # Individual migration files
│   │   │   ├── models/            # SQLAlchemy ORM models
│   │   │   │   ├── __init__.py     # Database models initialization
│   │   │   │   ├── base.py         # Base ORM model classes
│   │   │   │   ├── phylo.py        # Phylogenetic data ORM models
│   │   │   │   ├── orthogroup.py   # Orthogroup ORM models
│   │   │   │   ├── species.py      # Species ORM models
│   │   │   │   ├── gene.py         # Gene ORM models
│   │   │   │   ├── user.py         # User ORM models
│   │   │   │   └── project.py      # Project ORM models
│   │   │   └── seeders/           # Database seeding scripts
│   │   │       ├── __init__.py     # Seeders package initialization
│   │   │       ├── base_seeder.py  # Base seeder class
│   │   │       ├── species_seeder.py # Species data seeding
│   │   │       └── sample_data_seeder.py # Sample analysis data
│   │   │
│   │   ├── core/                   # Core application infrastructure
│   │   │   ├── __init__.py         # Core package initialization
│   │   │   ├── config.py          # Configuration management
│   │   │   ├── logging.py         # Logging configuration and setup
│   │   │   ├── metrics.py         # Performance metrics collection
│   │   │   ├── monitoring.py      # Application monitoring
│   │   │   ├── security.py        # Security implementations
│   │   │   │   ├── authentication.py # Authentication mechanisms
│   │   │   │   ├── authorization.py  # Authorization policies
│   │   │   │   ├── encryption.py     # Data encryption utilities
│   │   │   │   └── validation.py     # Security validation
│   │   │   ├── cache.py           # Caching infrastructure
│   │   │   ├── events.py          # Event system implementation
│   │   │   ├── tasks.py           # Background task system
│   │   │   ├── email.py           # Email service integration
│   │   │   ├── storage.py         # File storage abstractions
│   │   │   └── utils.py           # Core utility functions
│   │   │
│   │   └── utils/                  # Utility functions and helpers
│   │       ├── __init__.py         # Utils package initialization
│   │       ├── ete3_compat.py     # ETE3 compatibility layer
│   │       ├── validators.py      # Data validation utilities
│   │       ├── converters.py      # Data format converters
│   │       ├── parsers.py         # File format parsers
│   │       ├── serializers.py     # Data serialization utilities
│   │       ├── decorators.py      # Custom decorators
│   │       ├── exceptions.py      # Utility exception classes
│   │       ├── helpers.py         # General helper functions
│   │       ├── constants.py       # Utility constants
│   │       ├── types.py           # Custom type definitions
│   │       ├── math_utils.py      # Mathematical utility functions
│   │       ├── string_utils.py    # String manipulation utilities
│   │       ├── date_utils.py      # Date and time utilities
│   │       ├── file_utils.py      # File system utilities
│   │       ├── network_utils.py   # Network-related utilities
│   │       └── bio_utils.py       # Bioinformatics-specific utilities
│   │
│   ├── tests/                      # Comprehensive test suite
│   │   ├── __init__.py            # Test package initialization
│   │   ├── conftest.py            # Pytest configuration and fixtures
│   │   ├── test_config.py         # Test environment configuration
│   │   ├── pytest.ini             # Pytest configuration file
│   │   ├── tox.ini                # Tox configuration for multi-environment testing
│   │   │
│   │   ├── fixtures/              # Test data and fixtures
│   │   │   ├── __init__.py        # Fixtures package initialization
│   │   │   ├── sample_trees.nwk   # Sample phylogenetic trees
│   │   │   ├── test_sequences.fa  # Test sequence data
│   │   │   ├── orthogroup_data.csv # Sample orthogroup classifications
│   │   │   ├── species_data.json  # Species taxonomy test data
│   │   │   ├── gene_annotations.gff # Gene annotation test files
│   │   │   ├── alignment_data.aln # Multiple sequence alignments
│   │   │   ├── distance_matrices.csv # Distance matrix test data
│   │   │   └── api_responses.json # Mock API response data
│   │   │
│   │   ├── unit/                  # Unit test implementations
│   │   │   ├── __init__.py        # Unit tests package initialization
│   │   │   ├── test_models.py     # Data model unit tests
│   │   │   ├── test_schemas.py    # Schema validation unit tests
│   │   │   ├── test_services/     # Service layer unit tests
│   │   │   │   ├── __init__.py    # Service tests initialization
│   │   │   │   ├── test_phylogenetic.py # Phylogenetic service tests
│   │   │   │   ├── test_orthogroup.py   # Orthogroup service tests
│   │   │   │   ├── test_sequence.py     # Sequence service tests
│   │   │   │   ├── test_data_processing.py # Data processing tests
│   │   │   │   ├── test_visualization.py   # Visualization tests
│   │   │   │   └── test_background_tasks.py # Background task tests
│   │   │   ├── test_repositories/ # Repository layer unit tests
│   │   │   │   ├── __init__.py    # Repository tests initialization
│   │   │   │   ├── test_phylo_repository.py # Phylo repository tests
│   │   │   │   ├── test_orthogroup_repository.py # Orthogroup repository tests
│   │   │   │   └── test_cache_repository.py # Cache repository tests
│   │   │   ├── test_utils.py      # Utility function unit tests
│   │   │   ├── test_core.py       # Core functionality unit tests
│   │   │   ├── test_parsers.py    # Parser unit tests
│   │   │   ├── test_validators.py # Validation unit tests
│   │   │   └── test_converters.py # Converter unit tests
│   │   │
│   │   ├── integration/           # Integration test implementations
│   │   │   ├── __init__.py        # Integration tests package initialization
│   │   │   ├── test_api_phylo.py  # Phylogenetic API integration tests
│   │   │   ├── test_api_orthogroups.py # Orthogroup API integration tests
│   │   │   ├── test_api_species.py     # Species API integration tests
│   │   │   ├── test_api_upload.py      # Upload API integration tests
│   │   │   ├── test_database.py   # Database integration tests
│   │   │   ├── test_services.py   # Service integration tests
│   │   │   ├── test_workflow.py   # End-to-end workflow tests
│   │   │   ├── test_external_apis.py # External API integration tests
│   │   │   ├── test_file_processing.py # File processing integration tests
│   │   │   └── test_cache_integration.py # Cache integration tests
│   │   │
│   │   ├── performance/           # Performance and benchmark tests
│   │   │   ├── __init__.py        # Performance tests package initialization
│   │   │   ├── test_scalability.py # Scalability benchmark tests
│   │   │   ├── test_memory.py     # Memory usage optimization tests
│   │   │   ├── test_cpu.py        # CPU performance tests
│   │   │   ├── test_io.py         # I/O performance tests
│   │   │   ├── test_database_performance.py # Database performance tests
│   │   │   ├── test_api_performance.py      # API performance tests
│   │   │   ├── test_large_datasets.py       # Large dataset processing tests
│   │   │   ├── test_concurrent_analysis.py  # Concurrent analysis tests
│   │   │   ├── benchmarks/        # Performance benchmark suites
│   │   │   │   ├── __init__.py    # Benchmarks initialization
│   │   │   │   ├── phylo_benchmarks.py # Phylogenetic analysis benchmarks
│   │   │   │   ├── ortho_benchmarks.py # Orthogroup analysis benchmarks
│   │   │   │   └── api_benchmarks.py   # API endpoint benchmarks
│   │   │   └── load_testing/      # Load testing implementations
│   │   │       ├── __init__.py    # Load testing initialization
│   │   │       ├── api_load_tests.py # API load testing
│   │   │       ├── database_load_tests.py # Database load testing
│   │   │       └── concurrent_user_tests.py # Concurrent user testing
│   │   │
│   │   ├── e2e/                   # End-to-end test implementations
│   │   │   ├── __init__.py        # E2E tests package initialization
│   │   │   ├── conftest.py        # E2E test configuration and fixtures
│   │   │   ├── test_complete_workflows.py # Complete user workflow tests
│   │   │   ├── test_phylogenetic_analysis.py # Phylogenetic analysis E2E tests
│   │   │   ├── test_orthogroup_classification.py # Orthogroup classification E2E
│   │   │   ├── test_data_upload_workflow.py # Data upload workflow tests
│   │   │   ├── test_visualization_workflow.py # Visualization workflow tests
│   │   │   ├── test_export_workflow.py # Data export workflow tests
│   │   │   ├── test_user_management.py # User management E2E tests
│   │   │   ├── test_project_management.py # Project management E2E tests
│   │   │   ├── test_collaboration.py # Collaboration feature tests
│   │   │   ├── browser_tests/     # Browser-based E2E tests
│   │   │   │   ├── __init__.py    # Browser tests initialization
│   │   │   │   ├── test_frontend_integration.py # Frontend integration tests
│   │   │   │   ├── test_user_interactions.py    # User interaction tests
│   │   │   │   ├── test_data_visualization.py   # Data visualization tests
│   │   │   │   ├── test_responsive_design.py    # Responsive design tests
│   │   │   │   ├── test_accessibility.py        # Accessibility compliance tests
│   │   │   │   └── test_cross_browser.py        # Cross-browser compatibility
│   │   │   └── api_workflow_tests/ # API workflow E2E tests
│   │   │       ├── __init__.py    # API workflow tests initialization
│   │   │       ├── test_analysis_pipelines.py # Analysis pipeline tests
│   │   │       ├── test_data_processing.py    # Data processing workflows
│   │   │       └── test_batch_operations.py   # Batch operation workflows
│   │   │
│   │   ├── security/              # Security testing implementations
│   │   │   ├── __init__.py        # Security tests package initialization
│   │   │   ├── test_authentication.py # Authentication security tests
│   │   │   ├── test_authorization.py  # Authorization security tests
│   │   │   ├── test_input_validation.py # Input validation security tests
│   │   │   ├── test_sql_injection.py    # SQL injection prevention tests
│   │   │   ├── test_xss_protection.py   # XSS protection tests
│   │   │   ├── test_csrf_protection.py  # CSRF protection tests
│   │   │   ├── test_data_encryption.py  # Data encryption tests
│   │   │   ├── test_api_security.py     # API security tests
│   │   │   └── test_file_upload_security.py # File upload security tests
│   │   │
│   │   └── regression/            # Regression testing implementations
│   │       ├── __init__.py        # Regression tests package initialization
│   │       ├── test_algorithm_consistency.py # Algorithm consistency tests
│   │       ├── test_performance_regression.py # Performance regression tests
│   │       ├── test_api_compatibility.py # API compatibility tests
│   │       ├── test_data_format_compatibility.py # Data format compatibility
│   │       └── baseline_results/  # Baseline results for regression testing
│   │           ├── phylo_baselines.json # Phylogenetic analysis baselines
│   │           ├── ortho_baselines.json # Orthogroup classification baselines
│   │           └── performance_baselines.json # Performance baselines
│   │
│   ├── scripts/                   # Operational and maintenance scripts
│   │   ├── __init__.py            # Scripts package initialization
│   │   ├── setup_environment.py   # Environment setup automation
│   │   ├── database/              # Database management scripts
│   │   │   ├── __init__.py        # Database scripts initialization
│   │   │   ├── create_database.py # Database creation script
│   │   │   ├── migrate_database.py # Database migration script
│   │   │   ├── seed_database.py   # Database seeding script
│   │   │   ├── backup_database.py # Database backup script
│   │   │   ├── restore_database.py # Database restoration script
│   │   │   └── cleanup_database.py # Database cleanup script
│   │   ├── data_management/       # Data management scripts
│   │   │   ├── __init__.py        # Data management initialization
│   │   │   ├── import_species_data.py # Species data import
│   │   │   ├── import_gene_data.py    # Gene data import
│   │   │   ├── validate_data.py       # Data validation script
│   │   │   ├── convert_formats.py     # Data format conversion
│   │   │   └── cleanup_orphaned_data.py # Orphaned data cleanup
│   │   ├── deployment/            # Deployment and production scripts
│   │   │   ├── __init__.py        # Deployment scripts initialization
│   │   │   ├── deploy_production.py # Production deployment
│   │   │   ├── deploy_staging.py     # Staging deployment
│   │   │   ├── health_check.py       # System health monitoring
│   │   │   ├── log_analysis.py       # Log analysis and monitoring
│   │   │   └── performance_monitoring.py # Performance monitoring
│   │   ├── testing/               # Testing automation scripts
│   │   │   ├── __init__.py        # Testing scripts initialization
│   │   │   ├── run_all_tests.py   # Comprehensive test execution
│   │   │   ├── run_unit_tests.py  # Unit test execution
│   │   │   ├── run_integration_tests.py # Integration test execution
│   │   │   ├── run_performance_tests.py # Performance test execution
│   │   │   ├── run_e2e_tests.py   # End-to-end test execution
│   │   │   ├── generate_coverage_report.py # Coverage report generation
│   │   │   ├── benchmark_analysis.py # Benchmark analysis script
│   │   │   └── test_data_generator.py # Test data generation
│   │   ├── maintenance/           # Maintenance and operations scripts
│   │   │   ├── __init__.py        # Maintenance scripts initialization
│   │   │   ├── backup_system.py   # System backup automation
│   │   │   ├── update_dependencies.py # Dependency update procedures
│   │   │   ├── security_scan.py   # Security vulnerability scanning
│   │   │   ├── performance_audit.py # Performance auditing
│   │   │   ├── log_rotation.py    # Log rotation management
│   │   │   └── cache_management.py # Cache management utilities
│   │   └── development/           # Development utility scripts
│   │       ├── __init__.py        # Development scripts initialization
│   │       ├── setup_dev_environment.py # Development environment setup
│   │       ├── generate_test_data.py # Test data generation
│   │       ├── code_quality_check.py # Code quality analysis
│   │       ├── documentation_generator.py # Documentation generation
│   │       ├── api_documentation.py # API documentation generation
│   │       └── dependency_analysis.py # Dependency analysis
│   │
│   ├── docs/                      # Backend-specific documentation
│   │   ├── __init__.py            # Documentation package initialization
│   │   ├── api/                   # API documentation
│   │   │   ├── overview.md        # API overview and introduction
│   │   │   ├── authentication.md  # Authentication documentation
│   │   │   ├── endpoints/         # Individual endpoint documentation
│   │   │   │   ├── phylogenetic.md # Phylogenetic API documentation
│   │   │   │   ├── orthogroups.md  # Orthogroup API documentation
│   │   │   │   ├── species.md      # Species API documentation
│   │   │   │   ├── upload.md       # Upload API documentation
│   │   │   │   └── export.md       # Export API documentation
│   │   │   ├── examples/          # API usage examples
│   │   │   │   ├── python_client.py # Python client examples
│   │   │   │   ├── curl_examples.sh # cURL usage examples
│   │   │   │   └── postman_collection.json # Postman collection
│   │   │   └── specifications/    # API specifications
│   │   │       ├── openapi.yaml   # OpenAPI specification
│   │   │       └── asyncapi.yaml  # AsyncAPI specification
│   │   ├── architecture/          # Architecture documentation
│   │   │   ├── overview.md        # System architecture overview
│   │   │   ├── database_design.md # Database schema documentation
│   │   │   ├── service_architecture.md # Service layer architecture
│   │   │   ├── security_architecture.md # Security architecture
│   │   │   ├── scalability.md     # Scalability considerations
│   │   │   └── deployment_architecture.md # Deployment architecture
│   │   ├── development/           # Development documentation
│   │   │   ├── setup_guide.md     # Development environment setup
│   │   │   ├── coding_standards.md # Coding standards and conventions
│   │   │   ├── testing_guide.md   # Testing methodology and guidelines
│   │   │   ├── debugging_guide.md # Debugging procedures
│   │   │   ├── performance_optimization.md # Performance optimization
│   │   │   └── contribution_workflow.md # Contribution procedures
│   │   ├── algorithms/            # Algorithm documentation
│   │   │   ├── phylogenetic_analysis.md # Phylogenetic algorithms
│   │   │   ├── orthogroup_classification.md # Orthogroup algorithms
│   │   │   ├── sequence_analysis.md # Sequence analysis methods
│   │   │   ├── statistical_methods.md # Statistical analysis methods
│   │   │   └── performance_benchmarks.md # Algorithm benchmarks
│   │   ├── deployment/            # Deployment documentation
│   │   │   ├── production_deployment.md # Production deployment guide
│   │   │   ├── staging_deployment.md # Staging deployment guide
│   │   │   ├── docker_guide.md    # Docker deployment guide
│   │   │   ├── kubernetes_guide.md # Kubernetes deployment guide
│   │   │   ├── monitoring_setup.md # Monitoring and alerting setup
│   │   │   └── backup_procedures.md # Backup and recovery procedures
│   │   └── troubleshooting/       # Troubleshooting guides
│   │       ├── common_issues.md   # Common issues and solutions
│   │       ├── performance_issues.md # Performance troubleshooting
│   │       ├── database_issues.md # Database troubleshooting
│   │       ├── api_issues.md      # API troubleshooting
│   │       └── deployment_issues.md # Deployment troubleshooting
│   │
│   ├── migrations/                # Database migration files (if using raw SQL)
│   │   ├── 001_initial_schema.sql # Initial database schema
│   │   ├── 002_add_phylo_tables.sql # Phylogenetic tables addition
│   │   ├── 003_add_orthogroup_tables.sql # Orthogroup tables addition
│   │   └── 004_add_user_tables.sql # User management tables
│   │
│   └── config/                    # Configuration files
│       ├── __init__.py            # Configuration package initialization
│       ├── settings/              # Environment-specific settings
│       │   ├── __init__.py        # Settings initialization
│       │   ├── base.py            # Base configuration settings
│       │   ├── development.py     # Development environment settings
│       │   ├── testing.py         # Testing environment settings
│       │   ├── staging.py         # Staging environment settings
│       │   └── production.py      # Production environment settings
│       ├── logging/               # Logging configuration
│       │   ├── development.yaml   # Development logging config
│       │   ├── testing.yaml       # Testing logging config
│       │   ├── staging.yaml       # Staging logging config
│       │   └── production.yaml    # Production logging config
│       └── database/              # Database configuration
│           ├── development.yaml   # Development database config
│           ├── testing.yaml       # Testing database config
│           ├── staging.yaml       # Staging database config
│           └── production.yaml    # Production database config
│
├── frontend/                      # Frontend application
│   ├── README.md                  # Frontend-specific documentation
│   ├── package.json               # Node.js dependencies and scripts
│   ├── package-lock.json          # Locked dependency versions
│   ├── tsconfig.json              # TypeScript configuration
│   ├── tsconfig.node.json         # Node.js TypeScript configuration
│   ├── vite.config.ts             # Vite build tool configuration
│   ├── vitest.config.ts           # Vitest testing configuration
│   ├── tailwind.config.js         # Tailwind CSS configuration
│   ├── postcss.config.js          # PostCSS configuration
│   ├── eslint.config.js           # ESLint configuration
│   ├── prettier.config.js         # Prettier configuration
│   ├── jest.config.js             # Jest testing configuration
│   ├── cypress.config.ts          # Cypress E2E testing configuration
│   ├── playwright.config.ts       # Playwright E2E testing configuration
│   ├── .env                       # Environment variables template
│   ├── .env.local                 # Local environment variables
│   ├── .env.development           # Development environment variables
│   ├── .env.production            # Production environment variables
│   ├── index.html                 # Main HTML entry point
│   │
│   ├── public/                    # Static assets
│   │   ├── favicon.ico            # Application favicon
│   │   ├── manifest.json          # Web app manifest
│   │   ├── robots.txt             # Search engine robots configuration
│   │   ├── icons/                 # Application icons
│   │   │   ├── icon-192x192.png   # PWA icon 192x192
│   │   │   ├── icon-512x512.png   # PWA icon 512x512
│   │   │   └── apple-touch-icon.png # Apple touch icon
│   │   ├── images/                # Static images
│   │   │   ├── logo.svg           # Application logo
│   │   │   ├── placeholder.png    # Placeholder images
│   │   │   └── backgrounds/       # Background images
│   │   └── fonts/                 # Custom fonts
│   │       ├── inter.woff2        # Inter font family
│   │       └── roboto-mono.woff2  # Monospace font
│   │
│   ├── src/                       # Frontend source code
│   │   ├── main.tsx               # Application entry point
│   │   ├── App.tsx                # Root application component
│   │   ├── vite-env.d.ts          # Vite environment type definitions
│   │   │
│   │   ├── components/            # Reusable React components
│   │   │   ├── index.ts           # Component exports
│   │   │   ├── common/            # Common/shared components
│   │   │   │   ├── Button/        # Button component
│   │   │   │   │   ├── Button.tsx # Button implementation
│   │   │   │   │   ├── Button.test.tsx # Button tests
│   │   │   │   │   ├── Button.stories.tsx # Storybook stories
│   │   │   │   │   └── index.ts   # Button exports
│   │   │   │   ├── Input/         # Input component
│   │   │   │   ├── Modal/         # Modal component
│   │   │   │   ├── Loading/       # Loading spinner component
│   │   │   │   ├── ErrorBoundary/ # Error boundary component
│   │   │   │   ├── Layout/        # Layout components
│   │   │   │   └── Navigation/    # Navigation components
│   │   │   ├── forms/             # Form components
│   │   │   │   ├── PhyloAnalysisForm/ # Phylogenetic analysis form
│   │   │   │   ├── OrthogroupForm/    # Orthogroup classification form
│   │   │   │   ├── UploadForm/        # File upload form
│   │   │   │   └── SearchForm/        # Search form component
│   │   │   ├── visualization/     # Data visualization components
│   │   │   │   ├── PhylogeneticTree/  # Phylogenetic tree viewer
│   │   │   │   │   ├── TreeViewer.tsx # Main tree viewer component
│   │   │   │   │   ├── TreeNode.tsx   # Individual tree node component
│   │   │   │   │   ├── TreeControls.tsx # Tree control panel
│   │   │   │   │   ├── TreeLegend.tsx   # Tree legend component
│   │   │   │   │   └── hooks/          # Tree-specific hooks
│   │   │   │   ├── OrthogroupVisualization/ # Orthogroup visualization
│   │   │   │   ├── SequenceAlignment/      # Sequence alignment viewer
│   │   │   │   ├── StatisticsCharts/       # Statistical charts
│   │   │   │   └── DataTables/             # Data table components
│   │   │   ├── analysis/          # Analysis-specific components
│   │   │   │   ├── AnalysisResults/   # Analysis results display
│   │   │   │   ├── AnalysisHistory/   # Analysis history component
│   │   │   │   ├── AnalysisComparison/ # Analysis comparison tool
│   │   │   │   └── AnalysisExport/     # Analysis export component
│   │   │   └── admin/             # Administrative components
│   │   │       ├── UserManagement/   # User management interface
│   │   │       ├── SystemMonitoring/ # System monitoring dashboard
│   │   │       └── DataManagement/   # Data management interface
│   │   │
│   │   ├── pages/                 # Application pages/routes
│   │   │   ├── index.ts           # Page exports
│   │   │   ├── HomePage/          # Landing page
│   │   │   │   ├── HomePage.tsx   # Home page component
│   │   │   │   ├── HomePage.test.tsx # Home page tests
│   │   │   │   └── components/    # Home page specific components
│   │   │   ├── AnalysisPage/      # Analysis page
│   │   │   │   ├── AnalysisPage.tsx # Analysis page component
│   │   │   │   └── components/    # Analysis page components
│   │   │   ├── OrthogroupPage/    # Orthogroup analysis page
│   │   │   ├── UploadPage/        # Data upload page
│   │   │   ├── ResultsPage/       # Results display page
│   │   │   ├── ProfilePage/       # User profile page
│   │   │   ├── ProjectsPage/      # Projects management page
│   │   │   ├── DocumentationPage/ # Documentation page
│   │   │   ├── AboutPage/         # About page
│   │   │   ├── ContactPage/       # Contact page
│   │   │   ├── LoginPage/         # User login page
│   │   │   ├── RegisterPage/      # User registration page
│   │   │   ├── DashboardPage/     # User dashboard
│   │   │   ├── AdminPage/         # Administrative interface
│   │   │   ├── SettingsPage/      # Application settings
│   │   │   ├── HelpPage/          # Help and support
│   │   │   └── NotFoundPage/      # 404 error page
│   │   │
│   │   ├── services/              # API communication and external services
│   │   │   ├── index.ts           # Service exports
│   │   │   ├── api/               # API communication services
│   │   │   │   ├── client.ts      # Base API client configuration
│   │   │   │   ├── types.ts       # API type definitions
│   │   │   │   ├── phyloApi.ts    # Phylogenetic analysis API
│   │   │   │   ├── orthogroupApi.ts # Orthogroup classification API
│   │   │   │   ├── speciesApi.ts  # Species management API
│   │   │   │   ├── uploadApi.ts   # File upload API
│   │   │   │   ├── userApi.ts     # User management API
│   │   │   │   ├── projectApi.ts  # Project management API
│   │   │   │   └── searchApi.ts   # Search API
│   │   │   ├── auth/              # Authentication services
│   │   │   │   ├── authService.ts # Authentication service
│   │   │   │   ├── tokenService.ts # Token management
│   │   │   │   └── permissions.ts # Permission management
│   │   │   ├── cache/             # Caching services
│   │   │   │   ├── cacheService.ts # Client-side caching
│   │   │   │   └── storageService.ts # Local storage management
│   │   │   ├── notifications/     # Notification services
│   │   │   │   ├── notificationService.ts # Notification management
│   │   │   │   └── toastService.ts # Toast notifications
│   │   │   ├── analytics/         # Analytics services
│   │   │   │   ├── analyticsService.ts # Usage analytics
│   │   │   │   └── errorTracking.ts # Error tracking
│   │   │   └── external/          # External service integrations
│   │   │       ├── fileStorage.ts # External file storage
│   │   │       └── mapping.ts     # External mapping services
│   │   │
│   │   ├── hooks/                 # Custom React hooks
│   │   │   ├── index.ts           # Hook exports
│   │   │   ├── common/            # Common hooks
│   │   │   │   ├── useLocalStorage.ts # Local storage hook
│   │   │   │   ├── useDebounce.ts     # Debounce hook
│   │   │   │   ├── useAsync.ts        # Async operation hook
│   │   │   │   ├── useToggle.ts       # Toggle state hook
│   │   │   │   └── useWindowSize.ts   # Window size hook
│   │   │   ├── api/               # API-related hooks
│   │   │   │   ├── usePhyloApi.ts     # Phylogenetic API hooks
│   │   │   │   ├── useOrthogroupApi.ts # Orthogroup API hooks
│   │   │   │   ├── useUploadApi.ts    # Upload API hooks
│   │   │   │   └── useSearchApi.ts    # Search API hooks
│   │   │   ├── auth/              # Authentication hooks
│   │   │   │   ├── useAuth.ts         # Authentication hook
│   │   │   │   ├── useUser.ts         # User data hook
│   │   │   │   └── usePermissions.ts  # Permissions hook
│   │   │   ├── visualization/     # Visualization hooks
│   │   │   │   ├── useTreeVisualization.ts # Tree visualization hook
│   │   │   │   ├── useChartData.ts         # Chart data hook
│   │   │   │   └── useInteractiveTree.ts   # Interactive tree hook
│   │   │   └── analysis/          # Analysis hooks
│   │   │       ├── useAnalysisState.ts # Analysis state management
│   │   │       ├── useResultsCache.ts  # Results caching hook
│   │   │       └── useAnalysisHistory.ts # Analysis history hook
│   │   │
│   │   ├── store/                 # State management
│   │   │   ├── index.ts           # Store configuration and exports
│   │   │   ├── rootReducer.ts     # Root reducer combination
│   │   │   ├── middleware.ts      # Custom middleware
│   │   │   ├── slices/            # Redux Toolkit slices
│   │   │   │   ├── authSlice.ts   # Authentication state
│   │   │   │   ├── analysisSlice.ts # Analysis state
│   │   │   │   ├── orthogroupSlice.ts # Orthogroup state
│   │   │   │   ├── uiSlice.ts     # UI state management
│   │   │   │   ├── userSlice.ts   # User data state
│   │   │   │   ├── projectSlice.ts # Project state
│   │   │   │   └── notificationSlice.ts # Notification state
│   │   │   ├── selectors/         # Reselect selectors
│   │   │   │   ├── authSelectors.ts # Authentication selectors
│   │   │   │   ├── analysisSelectors.ts # Analysis selectors
│   │   │   │   └── uiSelectors.ts # UI selectors
│   │   │   └── thunks/            # Async thunks
│   │   │       ├── authThunks.ts  # Authentication async actions
│   │   │       ├── analysisThunks.ts # Analysis async actions
│   │   │       └── dataThunks.ts  # Data fetching async actions
│   │   │
│   │   ├── utils/                 # Utility functions and helpers
│   │   │   ├── index.ts           # Utility exports
│   │   │   ├── constants.ts       # Application constants
│   │   │   ├── types.ts           # Global type definitions
│   │   │   ├── helpers/           # Helper functions
│   │   │   │   ├── dateHelpers.ts # Date manipulation helpers
│   │   │   │   ├── stringHelpers.ts # String manipulation helpers
│   │   │   │   ├── mathHelpers.ts   # Mathematical helpers
│   │   │   │   ├── arrayHelpers.ts  # Array manipulation helpers
│   │   │   │   └── objectHelpers.ts # Object manipulation helpers
│   │   │   ├── validation/        # Validation utilities
│   │   │   │   ├── schemas.ts     # Validation schemas
│   │   │   │   ├── validators.ts  # Custom validators
│   │   │   │   └── formValidation.ts # Form validation utilities
│   │   │   ├── formatting/        # Data formatting utilities
│   │   │   │   ├── numberFormatters.ts # Number formatting
│   │   │   │   ├── dateFormatters.ts   # Date formatting
│   │   │   │   └── fileFormatters.ts   # File formatting
│   │   │   ├── api/               # API utility functions
│   │   │   │   ├── requestUtils.ts # Request utilities
│   │   │   │   ├── responseUtils.ts # Response utilities
│   │   │   │   └── errorHandlers.ts # Error handling utilities
│   │   │   ├── bio/               # Bioinformatics utilities
│   │   │   │   ├── newickParser.ts # Newick format parser
│   │   │   │   ├── sequenceUtils.ts # Sequence manipulation
│   │   │   │   ├── treeUtils.ts     # Tree manipulation utilities
│   │   │   │   └── dataConverters.ts # Data format converters
│   │   │   └── testing/           # Testing utilities
│   │   │       ├── testUtils.ts   # Test helper functions
│   │   │       ├── mockData.ts    # Mock data generators
│   │   │       ├── renderUtils.ts # Test rendering utilities
│   │   │       └── apiMocks.ts    # API mocking utilities
│   │   │
│   │   ├── styles/                # Global styles and themes
│   │   │   ├── index.css          # Main stylesheet entry point
│   │   │   ├── globals.css        # Global CSS styles
│   │   │   ├── variables.css      # CSS custom properties
│   │   │   ├── components.css     # Component-specific styles
│   │   │   ├── utilities.css      # Utility classes
│   │   │   ├── themes/            # Theme definitions
│   │   │   │   ├── light.css      # Light theme
│   │   │   │   ├── dark.css       # Dark theme
│   │   │   │   └── highContrast.css # High contrast theme
│   │   │   ├── layouts/           # Layout-specific styles
│   │   │   │   ├── header.css     # Header layout styles
│   │   │   │   ├── sidebar.css    # Sidebar layout styles
│   │   │   │   └── footer.css     # Footer layout styles
│   │   │   └── vendor/            # Third-party library styles
│   │   │       ├── d3-overrides.css # D3.js style overrides
│   │   │       └── mui-overrides.css # Material-UI overrides
│   │   │
│   │   ├── assets/                # Static assets imported by code
│   │   │   ├── icons/             # SVG icons
│   │   │   │   ├── phylo-icon.svg # Phylogenetic analysis icon
│   │   │   │   ├── ortho-icon.svg # Orthogroup analysis icon
│   │   │   │   └── common/        # Common icons
│   │   │   ├── images/            # Application images
│   │   │   │   ├── logo.svg       # Application logo
│   │   │   │   ├── hero-bg.jpg    # Hero background image
│   │   │   │   └── placeholders/  # Placeholder images
│   │   │   ├── animations/        # Animation files
│   │   │   │   ├── loading.json   # Loading animation (Lottie)
│   │   │   │   └── success.json   # Success animation
│   │   │   └── data/              # Static data files
│   │   │       ├── sample-tree.nwk # Sample phylogenetic tree
│   │   │       ├── species-list.json # Species reference data
│   │   │       └── help-content.json # Help content data
│   │   │
│   │   └── types/                 # TypeScript type definitions
│   │       ├── index.ts           # Type exports
│   │       ├── api.ts             # API-related types
│   │       ├── auth.ts            # Authentication types
│   │       ├── analysis.ts        # Analysis-related types
│   │       ├── phylo.ts           # Phylogenetic analysis types
│   │       ├── orthogroup.ts      # Orthogroup types
│   │       ├── species.ts         # Species types
│   │       ├── user.ts            # User types
│   │       ├── project.ts         # Project types
│   │       ├── ui.ts              # UI component types
│   │       ├── visualization.ts   # Visualization types
│   │       ├── global.d.ts        # Global type declarations
│   │       └── environment.d.ts   # Environment variable types
│   │
│   ├── tests/                     # Frontend test suite
│   │   ├── setup.ts               # Test setup configuration
│   │   ├── jest.setup.ts          # Jest setup file
│   │   ├── vitest.setup.ts        # Vitest setup configuration
│   │   ├── test-utils.tsx         # Testing utility functions
│   │   ├── mocks/                 # Test mocks and fixtures
│   │   │   ├── apiMocks.ts        # API response mocks
│   │   │   ├── dataMocks.ts       # Test data mocks
│   │   │   ├── componentMocks.ts  # Component mocks
│   │   │   └── serviceMocks.ts    # Service mocks
│   │   ├── unit/                  # Unit tests
│   │   │   ├── components/        # Component unit tests
│   │   │   │   ├── common/        # Common component tests
│   │   │   │   ├── forms/         # Form component tests
│   │   │   │   ├── visualization/ # Visualization component tests
│   │   │   │   └── analysis/      # Analysis component tests
│   │   │   ├── hooks/             # Custom hooks tests
│   │   │   ├── services/          # Service layer tests
│   │   │   ├── utils/             # Utility function tests
│   │   │   └── store/             # State management tests
│   │   ├── integration/           # Integration tests
│   │   │   ├── api/               # API integration tests
│   │   │   ├── components/        # Component integration tests
│   │   │   ├── workflows/         # User workflow tests
│   │   │   └── authentication/    # Authentication flow tests
│   │   ├── e2e/                   # End-to-end tests
│   │   │   ├── specs/             # E2E test specifications
│   │   │   │   ├── analysis-workflow.spec.ts # Analysis workflow E2E
│   │   │   │   ├── upload-workflow.spec.ts   # Upload workflow E2E
│   │   │   │   ├── visualization.spec.ts     # Visualization E2E
│   │   │   │   └── user-management.spec.ts   # User management E2E
│   │   │   ├── fixtures/          # E2E test fixtures
│   │   │   ├── page-objects/      # Page object models
│   │   │   └── support/           # E2E test support files
│   │   ├── accessibility/         # Accessibility tests
│   │   │   ├── axe-tests.spec.ts  # Axe accessibility tests
│   │   │   ├── keyboard-nav.spec.ts # Keyboard navigation tests
│   │   │   └── screen-reader.spec.ts # Screen reader tests
│   │   ├── performance/           # Performance tests
│   │   │   ├── lighthouse.spec.ts # Lighthouse performance tests
│   │   │   ├── bundle-size.spec.ts # Bundle size tests
│   │   │   └── render-performance.spec.ts # Render performance tests
│   │   └── visual/                # Visual regression tests
│   │       ├── storybook-tests/   # Storybook visual tests
│   │       ├── screenshots/       # Reference screenshots
│   │       └── percy-tests/       # Percy visual tests
│   │
│   ├── .storybook/                # Storybook configuration
│   │   ├── main.ts                # Storybook main configuration
│   │   ├── preview.ts             # Storybook preview configuration
│   │   ├── manager.ts             # Storybook manager configuration
│   │   └── addons.ts              # Storybook addons configuration
│   │
│   ├── docs/                      # Frontend documentation
│   │   ├── README.md              # Frontend setup and development guide
│   │   ├── ARCHITECTURE.md        # Frontend architecture documentation
│   │   ├── COMPONENTS.md          # Component library documentation
│   │   ├── TESTING.md             # Testing strategy and guidelines
│   │   ├── DEPLOYMENT.md          # Deployment procedures
│   │   ├── components/            # Component documentation
│   │   │   ├── design-system.md   # Design system guidelines
│   │   │   ├── component-api.md   # Component API documentation
│   │   │   └── style-guide.md     # Styling guidelines
│   │   ├── development/           # Development guides
│   │   │   ├── setup-guide.md     # Development environment setup
│   │   │   ├── coding-standards.md # Frontend coding standards
│   │   │   ├── state-management.md # State management patterns
│   │   │   └── performance-optimization.md # Performance optimization
│   │   └── api-integration/       # API integration documentation
│   │       ├── api-client.md      # API client usage
│   │       ├── error-handling.md  # Error handling patterns
│   │       └── caching-strategy.md # Caching strategies
│   │
│   ├── scripts/                   # Frontend build and utility scripts
│   │   ├── build.js               # Custom build script
│   │   ├── analyze.js             # Bundle analysis script
│   │   ├── generate-types.js      # Type generation script
│   │   ├── update-dependencies.js # Dependency update script
│   │   └── deploy.js              # Deployment script
│   │
│   └── config/                    # Configuration files
│       ├── webpack/               # Webpack configurations
│       │   ├── webpack.common.js  # Common webpack config
│       │   ├── webpack.dev.js     # Development webpack config
│       │   └── webpack.prod.js    # Production webpack config
│       ├── babel/                 # Babel configurations
│       │   ├── babel.config.js    # Main babel configuration
│       │   └── babel.dev.js       # Development babel config
│       └── env/                   # Environment configurations
│           ├── development.env    # Development environment
│           ├── staging.env        # Staging environment
│           └── production.env     # Production environment
│
├── docs/                          # Project-wide documentation
│   ├── README.md                  # Main project documentation
│   ├── ARCHITECTURE.md            # System architecture overview
│   ├── API_DOCUMENTATION.md       # Comprehensive API documentation
│   ├── DEPLOYMENT_GUIDE.md        # Deployment procedures and guidelines
│   ├── CONTRIBUTING.md            # Contribution guidelines and workflow
│   ├── TESTING_STRATEGY.md        # Testing methodology and standards
│   ├── PERFORMANCE_BENCHMARKS.md  # Performance benchmarking results
│   ├── SECURITY_GUIDELINES.md     # Security best practices
│   ├── TROUBLESHOOTING.md         # Common issues and solutions
│   │
│   ├── architecture/              # Architectural documentation
│   │   ├── system-overview.md     # High-level system architecture
│   │   ├── microservices-design.md # Microservices architecture
│   │   ├── database-design.md     # Database schema and design
│   │   ├── api-design-principles.md # API design guidelines
│   │   ├── security-architecture.md # Security architecture overview
│   │   ├── scalability-strategy.md  # Scalability considerations
│   │   ├── data-flow-diagrams.md    # Data flow documentation
│   │   └── integration-patterns.md  # Integration architecture patterns
│   │
│   ├── scientific/                # Scientific documentation
│   │   ├── algorithms/            # Algorithm descriptions and references
│   │   │   ├── phylogenetic-reconstruction.md # Phylogenetic algorithms
│   │   │   ├── orthogroup-classification.md   # Orthogroup algorithms
│   │   │   ├── sequence-alignment.md          # Alignment algorithms
│   │   │   ├── statistical-methods.md         # Statistical analysis
│   │   │   └── distance-calculations.md       # Distance calculation methods
│   │   ├── validation/            # Scientific validation procedures
│   │   │   ├── algorithm-validation.md # Algorithm validation methods
│   │   │   ├── benchmark-datasets.md   # Benchmark dataset descriptions
│   │   │   ├── accuracy-metrics.md     # Accuracy measurement methods
│   │   │   └── cross-validation.md     # Cross-validation procedures
│   │   ├── benchmarks/            # Performance benchmarking
│   │   │   ├── computational-complexity.md # Complexity analysis
│   │   │   ├── performance-comparisons.md  # Tool comparisons
│   │   │   ├── scalability-tests.md        # Scalability benchmarks
│   │   │   └── memory-efficiency.md        # Memory usage analysis
│   │   └── use-cases/             # Scientific use cases and examples
│   │       ├── comparative-genomics.md # Comparative genomics workflows
│   │       ├── phylogenetic-analysis.md # Phylogenetic analysis examples
│   │       ├── orthogroup-studies.md    # Orthogroup classification studies
│   │       └── publication-examples.md  # Published research examples
│   │
│   ├── development/               # Development guidelines and procedures
│   │   ├── setup/                 # Development environment setup
│   │   │   ├── local-development.md # Local development setup
│   │   │   ├── docker-development.md # Docker-based development
│   │   │   ├── ide-configuration.md  # IDE setup and configuration
│   │   │   └── debugging-guide.md    # Debugging procedures
│   │   ├── coding-standards/      # Code quality and standards
│   │   │   ├── python-standards.md  # Python coding standards
│   │   │   ├── typescript-standards.md # TypeScript coding standards
│   │   │   ├── documentation-standards.md # Documentation standards
│   │   │   ├── commit-conventions.md # Git commit conventions
│   │   │   └── code-review-process.md # Code review procedures
│   │   ├── testing/               # Testing guidelines and procedures
│   │   │   ├── unit-testing-guide.md      # Unit testing guidelines
│   │   │   ├── integration-testing-guide.md # Integration testing
│   │   │   ├── e2e-testing-guide.md       # End-to-end testing
│   │   │   ├── performance-testing-guide.md # Performance testing
│   │   │   ├── test-data-management.md    # Test data procedures
│   │   │   └── continuous-testing.md      # Continuous testing setup
│   │   ├── deployment/            # Deployment procedures
│   │   │   ├── ci-cd-pipeline.md     # CI/CD pipeline documentation
│   │   │   ├── production-deployment.md # Production deployment
│   │   │   ├── staging-deployment.md    # Staging deployment
│   │   │   ├── rollback-procedures.md   # Rollback procedures
│   │   │   └── monitoring-setup.md      # Monitoring configuration
│   │   └── maintenance/           # Maintenance procedures
│   │       ├── dependency-updates.md # Dependency update procedures
│   │       ├── security-updates.md   # Security update procedures
│   │       ├── backup-procedures.md  # Backup and recovery
│   │       ├── performance-monitoring.md # Performance monitoring
│   │       └── incident-response.md     # Incident response procedures
│   │
│   ├── user-guides/               # User documentation
│   │   ├── getting-started.md     # Getting started guide
│   │   ├── user-manual.md         # Comprehensive user manual
│   │   ├── tutorials/             # Step-by-step tutorials
│   │   │   ├── phylogenetic-analysis-tutorial.md # Phylogenetic analysis
│   │   │   ├── orthogroup-classification-tutorial.md # Orthogroup classification
│   │   │   ├── data-upload-tutorial.md # Data upload procedures
│   │   │   └── visualization-tutorial.md # Data visualization
│   │   ├── api-reference/         # API usage documentation
│   │   │   ├── api-overview.md    # API overview and authentication
│   │   │   ├── endpoint-reference.md # Detailed endpoint documentation
│   │   │   ├── code-examples/     # Programming language examples
│   │   │   │   ├── python-examples.py # Python API usage examples
│   │   │   │   ├── r-examples.R       # R API usage examples
│   │   │   │   ├── curl-examples.sh   # cURL examples
│   │   │   │   └── javascript-examples.js # JavaScript examples
│   │   │   └── sdk-documentation/ # SDK documentation
│   │   │       ├── python-sdk.md  # Python SDK documentation
│   │   │       └── r-sdk.md       # R SDK documentation
│   │   └── troubleshooting/       # User troubleshooting guides
│   │       ├── common-issues.md   # Common user issues
│   │       ├── error-messages.md  # Error message explanations
│   │       ├── performance-tips.md # Performance optimization tips
│   │       └── faq.md             # Frequently asked questions
│   │
│   └── legal/                     # Legal and compliance documentation
│       ├── LICENSE.md             # Detailed license information
│       ├── privacy-policy.md      # Privacy policy
│       ├── terms-of-service.md    # Terms of service
│       ├── compliance/            # Compliance documentation
│       │   ├── gdpr-compliance.md # GDPR compliance measures
│       │   ├── accessibility-compliance.md # Accessibility compliance
│       │   └── security-compliance.md # Security compliance
│       └── third-party-licenses/  # Third-party license documentation
│           ├── backend-licenses.md # Backend dependency licenses
│           ├── frontend-licenses.md # Frontend dependency licenses
│           └── license-compatibility.md # License compatibility analysis
│
├── infrastructure/                # Infrastructure and deployment configurations
│   ├── docker/                    # Docker configurations
│   │   ├── dockerfiles/           # Custom Dockerfiles
│   │   │   ├── Dockerfile.backend # Backend production Dockerfile
│   │   │   ├── Dockerfile.frontend # Frontend production Dockerfile
│   │   │   ├── Dockerfile.nginx   # Nginx reverse proxy Dockerfile
│   │   │   └── Dockerfile.dev     # Development multi-service Dockerfile
│   │   ├── compose/               # Docker Compose configurations
│   │   │   ├── docker-compose.prod.yml # Production configuration
│   │   │   ├── docker-compose.dev.yml  # Development configuration
│   │   │   ├── docker-compose.test.yml # Testing configuration
│   │   │   └── docker-compose.monitoring.yml # Monitoring stack
│   │   └── scripts/               # Docker utility scripts
│   │       ├── build-images.sh    # Image building script
│   │       ├── push-images.sh     # Image pushing script
│   │       ├── cleanup-images.sh  # Image cleanup script
│   │       └── health-check.sh    # Container health check
│   │
│   ├── kubernetes/                # Kubernetes deployment manifests
│   │   ├── namespaces/            # Namespace definitions
│   │   │   ├── production.yaml    # Production namespace
│   │   │   ├── staging.yaml       # Staging namespace
│   │   │   └── development.yaml   # Development namespace
│   │   ├── deployments/           # Deployment manifests
│   │   │   ├── backend-deployment.yaml # Backend deployment
│   │   │   ├── frontend-deployment.yaml # Frontend deployment
│   │   │   ├── nginx-deployment.yaml   # Nginx deployment
│   │   │   └── database-deployment.yaml # Database deployment
│   │   ├── services/              # Service definitions
│   │   │   ├── backend-service.yaml  # Backend service
│   │   │   ├── frontend-service.yaml # Frontend service
│   │   │   ├── nginx-service.yaml    # Nginx service
│   │   │   └── database-service.yaml # Database service
│   │   ├── ingress/               # Ingress configurations
│   │   │   ├── production-ingress.yaml # Production ingress
│   │   │   ├── staging-ingress.yaml    # Staging ingress
│   │   │   └── ssl-certificates.yaml   # SSL certificate configs
│   │   ├── configmaps/            # Configuration maps
│   │   │   ├── backend-config.yaml  # Backend configuration
│   │   │   ├── frontend-config.yaml # Frontend configuration
│   │   │   └── nginx-config.yaml    # Nginx configuration
│   │   ├── secrets/               # Secret definitions
│   │   │   ├── database-secrets.yaml # Database credentials
│   │   │   ├── api-secrets.yaml      # API keys and secrets
│   │   │   └── ssl-secrets.yaml      # SSL certificates
│   │   ├── volumes/               # Persistent volume definitions
│   │   │   ├── database-pv.yaml      # Database persistent volume
│   │   │   └── file-storage-pv.yaml  # File storage volume
│   │   └── monitoring/            # Monitoring configurations
│   │       ├── prometheus-config.yaml # Prometheus configuration
│   │       ├── grafana-config.yaml    # Grafana configuration
│   │       └── alertmanager-config.yaml # Alert manager configuration
│   │
│   ├── terraform/                 # Infrastructure as Code
│   │   ├── modules/               # Terraform modules
│   │   │   ├── vpc/               # VPC module
│   │   │   ├── eks/               # EKS cluster module
│   │   │   ├── rds/               # RDS database module
│   │   │   ├── s3/                # S3 storage module
│   │   │   └── security-groups/   # Security groups module
│   │   ├── environments/          # Environment-specific configurations
│   │   │   ├── production/        # Production infrastructure
│   │   │   ├── staging/           # Staging infrastructure
│   │   │   └── development/       # Development infrastructure
│   │   ├── providers.tf           # Terraform providers
│   │   ├── variables.tf           # Variable definitions
│   │   ├── outputs.tf             # Output definitions
│   │   └── terraform.tfvars.example # Example variables file
│   │
│   ├── ansible/                   # Configuration management
│   │   ├── playbooks/             # Ansible playbooks
│   │   │   ├── site.yml           # Main site playbook
│   │   │   ├── deploy.yml         # Deployment playbook
│   │   │   ├── backup.yml         # Backup playbook
│   │   │   └── monitoring.yml     # Monitoring setup playbook
│   │   ├── roles/                 # Ansible roles
│   │   │   ├── common/            # Common configuration role
│   │   │   ├── docker/            # Docker installation role
│   │   │   ├── nginx/             # Nginx configuration role
│   │   │   ├── postgresql/        # PostgreSQL setup role
│   │   │   └── monitoring/        # Monitoring setup role
│   │   ├── inventories/           # Inventory files
│   │   │   ├── production.ini     # Production inventory
│   │   │   ├── staging.ini        # Staging inventory
│   │   │   └── development.ini    # Development inventory
│   │   └── group_vars/            # Group variables
│   │       ├── all.yml            # Variables for all hosts
│   │       ├── production.yml     # Production-specific variables
│   │       └── staging.yml        # Staging-specific variables
│   │
│   ├── monitoring/                # Monitoring and observability
│   │   ├── prometheus/            # Prometheus configuration
│   │   │   ├── prometheus.yml     # Main Prometheus config
│   │   │   ├── alerting-rules.yml # Alerting rules
│   │   │   └── recording-rules.yml # Recording rules
│   │   ├── grafana/               # Grafana configuration
│   │   │   ├── dashboards/        # Custom dashboards
│   │   │   │   ├── application-dashboard.json # Application metrics
│   │   │   │   ├── infrastructure-dashboard.json # Infrastructure metrics
│   │   │   │   └── business-dashboard.json # Business metrics
│   │   │   ├── datasources/       # Data source configurations
│   │   │   └── grafana.ini        # Grafana configuration
│   │   ├── alertmanager/          # Alert manager configuration
│   │   │   ├── alertmanager.yml   # Main alertmanager config
│   │   │   └── notification-templates/ # Custom notification templates
│   │   ├── logs/                  # Log management
│   │   │   ├── fluentd/           # Fluentd configuration
│   │   │   ├── elasticsearch/     # Elasticsearch configuration
│   │   │   └── kibana/            # Kibana configuration
│   │   └── tracing/               # Distributed tracing
│   │       ├── jaeger/            # Jaeger configuration
│   │       └── zipkin/            # Zipkin configuration
│   │
│   ├── nginx/                     # Nginx configurations
│   │   ├── nginx.conf             # Main Nginx configuration
│   │   ├── sites-available/       # Available site configurations
│   │   │   ├── orthoviewer.conf   # Main application config
│   │   │   ├── api.conf           # API-specific config
│   │   │   └── monitoring.conf    # Monitoring endpoints config
│   │   ├── ssl/                   # SSL configurations
│   │   │   ├── ssl.conf           # SSL parameters
│   │   │   └── certs/             # SSL certificates directory
│   │   ├── security/              # Security configurations
│   │   │   ├── security-headers.conf # Security headers
│   │   │   └── rate-limiting.conf    # Rate limiting rules
│   │   └── optimization/          # Performance optimizations
│   │       ├── gzip.conf          # Gzip compression config
│   │       └── caching.conf       # Caching configuration
│   │
│   └── scripts/                   # Infrastructure utility scripts
│       ├── deployment/            # Deployment automation scripts
│       │   ├── deploy-production.sh # Production deployment script
│       │   ├── deploy-staging.sh    # Staging deployment script
│       │   ├── rollback.sh          # Rollback script
│       │   └── health-check.sh      # Post-deployment health check
│       ├── backup/                # Backup automation scripts
│       │   ├── backup-database.sh   # Database backup script
│       │   ├── backup-files.sh      # File backup script
│       │   └── restore-backup.sh    # Backup restoration script
│       ├── monitoring/            # Monitoring utility scripts
│       │   ├── setup-monitoring.sh # Monitoring stack setup
│       │   ├── alert-test.sh       # Alert testing script
│       │   └── log-analysis.sh     # Log analysis utilities
│       └── maintenance/           # Maintenance scripts
│           ├── system-update.sh   # System update automation
│           ├── cleanup.sh         # System cleanup script
│           ├── security-scan.sh   # Security scanning script
│           └── performance-audit.sh # Performance auditing
│
├── data/                          # Data files and samples
│   ├── sample-datasets/           # Sample biological datasets
│   │   ├── phylogenetic/          # Sample phylogenetic data
│   │   │   ├── vertebrate-tree.nwk # Vertebrate phylogenetic tree
│   │   │   ├── plant-phylogeny.nwk # Plant phylogenetic tree
│   │   │   └── microbial-tree.nwk  # Microbial phylogenetic tree
│   │   ├── orthogroups/           # Sample orthogroup data
│   │   │   ├── plant-orthogroups.tsv # Plant orthogroup classifications
│   │   │   ├── animal-orthogroups.tsv # Animal orthogroup classifications
│   │   │   └── fungal-orthogroups.tsv # Fungal orthogroup classifications
│   │   ├── sequences/             # Sample sequence data
│   │   │   ├── protein-sequences.fasta # Protein sequence samples
│   │   │   ├── dna-sequences.fasta     # DNA sequence samples
│   │   │   └── alignments.aln          # Multiple sequence alignments
│   │   └── annotations/           # Sample annotation data
│   │       ├── gene-annotations.gff # Gene annotation samples
│   │       ├── species-metadata.json # Species metadata
│   │       └── functional-annotations.tsv # Functional annotations
│   ├── reference-data/            # Reference biological data
│   │   ├── taxonomies/            # Taxonomic reference data
│   │   │   ├── ncbi-taxonomy.db   # NCBI taxonomy database
│   │   │   └── species-mappings.json # Species ID mappings
│   │   ├── databases/             # Reference database connections
│   │   │   ├── uniprot-config.json # UniProt database configuration
│   │   │   └── ncbi-config.json    # NCBI database configuration
│   │   └── standards/             # Data format standards
│   │       ├── newick-specification.md # Newick format specification
│   │       ├── fasta-specification.md  # FASTA format specification
│   │       └── gff-specification.md    # GFF format specification
│   ├── test-data/                 # Test-specific data
│   │   ├── unit-test-data/        # Unit test datasets
│   │   ├── integration-test-data/ # Integration test datasets
│   │   ├── performance-test-data/ # Performance test datasets
│   │   └── regression-test-data/  # Regression test datasets
│   └── user-uploads/              # User-uploaded data (gitignored)
│       ├── phylogenetic-trees/    # User phylogenetic tree uploads
│       ├── sequence-data/         # User sequence data uploads
│       └── annotation-files/      # User annotation file uploads
│
├── scripts/                       # Project-wide utility scripts
│   ├── setup/                     # Project setup and installation scripts
│   │   ├── install-dependencies.sh # Comprehensive dependency installation
│   │   ├── setup-development.sh    # Development environment setup
│   │   ├── setup-production.sh     # Production environment setup
│   │   ├── configure-git-hooks.sh  # Git hooks configuration
│   │   └── verify-installation.sh  # Installation verification
│   ├── build/                     # Build automation scripts
│   │   ├── build-all.sh           # Complete project build
│   │   ├── build-backend.sh       # Backend build script
│   │   ├── build-frontend.sh      # Frontend build script
│   │   ├── build-docs.sh          # Documentation build script
│   │   └── clean-build.sh         # Build artifact cleanup
│   ├── testing/                   # Testing automation scripts
│   │   ├── run-all-tests.sh       # Comprehensive test execution
│   │   ├── run-unit-tests.sh      # Unit test execution
│   │   ├── run-integration-tests.sh # Integration test execution
│   │   ├── run-e2e-tests.sh       # End-to-end test execution
│   │   ├── run-performance-tests.sh # Performance test execution
│   │   ├── run-security-tests.sh   # Security test execution
│   │   ├── generate-coverage.sh    # Test coverage generation
│   │   ├── test-report-generator.sh # Test report generation
│   │   └── continuous-testing.sh   # Continuous testing setup
│   ├── quality-assurance/         # Code quality and analysis scripts
│   │   ├── code-quality-check.sh  # Comprehensive code quality analysis
│   │   ├── security-audit.sh      # Security vulnerability assessment
│   │   ├── dependency-audit.sh    # Dependency security audit
│   │   ├── license-check.sh       # License compliance verification
│   │   ├── performance-audit.sh   # Performance analysis
│   │   └── accessibility-audit.sh # Accessibility compliance check
│   ├── data-management/           # Data management and migration scripts
│   │   ├── migrate-data.sh        # Data migration automation
│   │   ├── backup-data.sh         # Data backup procedures
│   │   ├── restore-data.sh        # Data restoration procedures
│   │   ├── validate-data.sh       # Data validation and integrity check
│   │   ├── cleanup-data.sh        # Data cleanup and optimization
│   │   └── sync-reference-data.sh # Reference data synchronization
│   ├── deployment/                # Deployment automation scripts
│   │   ├── deploy.sh              # Main deployment script
│   │   ├── deploy-staging.sh      # Staging deployment
│   │   ├── deploy-production.sh   # Production deployment
│   │   ├── rollback.sh            # Deployment rollback
│   │   ├── health-check.sh        # Post-deployment health verification
│   │   ├── smoke-test.sh          # Post-deployment smoke testing
│   │   └── deployment-notify.sh   # Deployment notification system
│   ├── monitoring/                # Monitoring and observability scripts
│   │   ├── setup-monitoring.sh    # Monitoring infrastructure setup
│   │   ├── health-monitor.sh      # Continuous health monitoring
│   │   ├── performance-monitor.sh # Performance monitoring
│   │   ├── log-analyzer.sh        # Log analysis and alerting
│   │   ├── metric-collector.sh    # Custom metric collection
│   │   └── alert-manager.sh       # Alert management automation
│   ├── maintenance/               # System maintenance scripts
│   │   ├── system-maintenance.sh  # Routine system maintenance
│   │   ├── update-dependencies.sh # Dependency update automation
│   │   ├── security-update.sh     # Security patch management
│   │   ├── cleanup-system.sh      # System cleanup and optimization
│   │   ├── log-rotation.sh        # Log rotation management
│   │   ├── cache-management.sh    # Cache maintenance
│   │   └── database-maintenance.sh # Database maintenance procedures
│   └── utilities/                 # General utility scripts
│       ├── project-stats.sh       # Project statistics generation
│       ├── dependency-graph.sh    # Dependency relationship analysis
│       ├── code-metrics.sh        # Code complexity and metrics analysis
│       ├── documentation-generator.sh # Automated documentation generation
│       ├── changelog-generator.sh # Changelog generation
│       ├── version-bumper.sh      # Version management automation
│       ├── git-hooks/             # Git hook implementations
│       │   ├── pre-commit         # Pre-commit hook
│       │   ├── pre-push           # Pre-push hook
│       │   ├── commit-msg         # Commit message validation
│       │   └── post-merge         # Post-merge hook
│       └── development-helpers/   # Development productivity scripts
│           ├── dev-environment-reset.sh # Development environment reset
│           ├── test-data-generator.sh   # Test data generation
│           ├── api-client-generator.sh  # API client generation
│           └── mock-data-server.sh      # Mock data server setup
│
├── .github/                       # GitHub-specific configurations
│   ├── workflows/                 # GitHub Actions workflows
│   │   ├── ci.yml                 # Continuous Integration workflow
│   │   ├── cd.yml                 # Continuous Deployment workflow
│   │   ├── test.yml               # Comprehensive testing workflow
│   │   ├── security-scan.yml      # Security scanning workflow
│   │   ├── dependency-update.yml  # Automated dependency updates
│   │   ├── performance-test.yml   # Performance testing workflow
│   │   ├── code-quality.yml       # Code quality analysis workflow
│   │   ├── documentation.yml      # Documentation generation workflow
│   │   ├── release.yml            # Release automation workflow
│   │   └── backup.yml             # Automated backup workflow
│   ├── ISSUE_TEMPLATE/            # GitHub issue templates
│   │   ├── bug_report.md          # Bug report template
│   │   ├── feature_request.md     # Feature request template
│   │   ├── scientific_enhancement.md # Scientific enhancement template
│   │   ├── performance_issue.md   # Performance issue template
│   │   └── documentation_request.md # Documentation request template
│   ├── PULL_REQUEST_TEMPLATE.md   # Pull request template
│   ├── CONTRIBUTING.md            # GitHub-specific contribution guidelines
│   ├── CODE_OF_CONDUCT.md         # Community code of conduct
│   ├── SECURITY.md                # Security policy and reporting
│   └── FUNDING.yml                # Funding and sponsorship information
│
├── .vscode/                       # Visual Studio Code configuration
│   ├── settings.json              # Workspace settings
│   ├── launch.json                # Debug configurations
│   ├── tasks.json                 # Task definitions
│   ├── extensions.json            # Recommended extensions
│   └── snippets/                  # Custom code snippets
│       ├── python.json            # Python snippets
│       ├── typescript.json        # TypeScript snippets
│       └── markdown.json          # Markdown snippets
│
├── .idea/                         # IntelliJ IDEA configuration
│   ├── runConfigurations/         # Run configurations
│   ├── inspectionProfiles/        # Code inspection profiles
│   └── codeStyles/                # Code style configurations
│
└── config/                        # Project-wide configuration
    ├── environments/              # Environment-specific configurations
    │   ├── development/           # Development environment
    │   │   ├── api.yaml           # API configuration
    │   │   ├── database.yaml      # Database configuration
    │   │   ├── logging.yaml       # Logging configuration
    │   │   ├── cache.yaml         # Cache configuration
    │   │   └── security.yaml      # Security configuration
    │   ├── testing/               # Testing environment
    │   │   ├── api.yaml           # Testing API configuration
    │   │   ├── database.yaml      # Testing database configuration
    │   │   ├── logging.yaml       # Testing logging configuration
    │   │   └── fixtures.yaml      # Test fixture configuration
    │   ├── staging/               # Staging environment
    │   │   ├── api.yaml           # Staging API configuration
    │   │   ├── database.yaml      # Staging database configuration
    │   │   ├── logging.yaml       # Staging logging configuration
    │   │   ├── monitoring.yaml    # Staging monitoring configuration
    │   │   └── security.yaml      # Staging security configuration
    │   └── production/            # Production environment
    │       ├── api.yaml           # Production API configuration
    │       ├── database.yaml      # Production database configuration
    │       ├── logging.yaml       # Production logging configuration
    │       ├── monitoring.yaml    # Production monitoring configuration
    │       ├── security.yaml      # Production security configuration
    │       ├── scaling.yaml       # Auto-scaling configuration
    │       └── backup.yaml        # Backup configuration
    ├── secrets/                   # Secret management templates
    │   ├── development.env.template # Development secrets template
    │   ├── staging.env.template     # Staging secrets template
    │   └── production.env.template  # Production secrets template
    ├── monitoring/                # Monitoring configuration templates
    │   ├── alerts.yaml            # Alert rule templates
    │   ├── dashboards.yaml        # Dashboard configuration templates
    │   └── metrics.yaml           # Custom metrics configuration
    ├── security/                  # Security configuration
    │   ├── security-policies.yaml # Security policy definitions
    │   ├── access-control.yaml    # Access control configurations
    │   ├── encryption.yaml        # Encryption configuration
    │   └── audit.yaml             # Audit logging configuration
    └── integration/               # External integration configurations
        ├── external-apis.yaml     # External API configurations
        ├── databases.yaml         # External database connections
        ├── messaging.yaml         # Message queue configurations
        └── storage.yaml           # External storage configurations
```

## Technology Stack and Dependencies

### Comprehensive Backend Technology Analysis

**Core Framework and Runtime Environment**

- **FastAPI 0.95.1**: Advanced Python web framework optimized for high-performance API development
  - Automatic API documentation generation using OpenAPI 3.0 specification
  - Native support for Python type hints with automatic validation
  - Asynchronous request handling with async/await syntax support
  - Built-in dependency injection system for scalable architecture
  - WebSocket support for real-time biological data streaming
  - Background task processing for long-running phylogenetic analyses

- **Python 3.10+**: Latest stable Python runtime with enhanced scientific computing features
  - Structural pattern matching for complex biological data processing
  - Enhanced type hints system for improved code documentation and IDE support
  - Performance optimizations including faster attribute access and function calls
  - Improved debugging capabilities with enhanced traceback information
  - Better memory management for large phylogenetic datasets

**Scientific Computing and Bioinformatics Libraries**

- **ETE3 Toolkit 3.1.3**: Comprehensive phylogenetic analysis framework
  - Advanced tree visualization and manipulation capabilities
  - Support for multiple tree formats (Newick, PhyloXML, NeXML)
  - Phylogenetic reconstruction algorithms including neighbor-joining and maximum likelihood
  - Tree comparison and consensus methods
  - Integration with external phylogenetic software packages
  - Evolutionary analysis tools including ancestral sequence reconstruction

- **NumPy 1.24.2**: Fundamental package for scientific computing with Python
  - N-dimensional array objects with broadcasting and vectorization capabilities
  - Comprehensive mathematical function library for biological computations
  - Linear algebra operations optimized for phylogenetic distance calculations
  - Random number generation for Monte Carlo simulations
  - Integration with compiled C/C++ and Fortran libraries for performance
  - Memory-efficient handling of large biological datasets

- **Pandas 2.0.0**: High-performance data manipulation and analysis library
  - DataFrame and Series data structures optimized for biological data
  - Advanced data cleaning and transformation capabilities
  - Time series analysis for temporal biological data
  - Statistical analysis and aggregation functions
  - Integration with multiple file formats (CSV, Excel, HDF5, Parquet)
  - Memory-efficient operations for large-scale comparative genomics datasets

**Data Validation and API Framework**

- **Pydantic 1.10.22**: Advanced data validation library using Python type annotations
  - Automatic data parsing with type coercion and validation
  - JSON Schema generation for comprehensive API documentation
  - Custom validators for biological data formats and constraints
  - Integration with FastAPI for request/response validation
  - Performance optimizations for high-throughput data processing
  - Support for complex nested data structures common in bioinformatics

**Web Server and Application Server Infrastructure**

- **Uvicorn 0.22.0**: Lightning-fast ASGI server implementation
  - High-performance HTTP/1.1 and HTTP/2 protocol support
  - WebSocket protocol support for real-time data streaming
  - Hot-reload capabilities for efficient development workflows
  - Multi-worker process management for production scalability
  - Integration with modern Python web frameworks
  - Resource monitoring and performance metrics collection

**Testing and Quality Assurance Framework**

- **Pytest 8.3.5**: Enterprise-grade testing framework with extensive plugin ecosystem
  - Advanced fixture system for complex test data management
  - Parametrized testing for comprehensive input scenario coverage
  - Property-based testing integration with Hypothesis
  - Performance benchmarking capabilities with pytest-benchmark
  - Coverage analysis and reporting with pytest-cov
  - Integration with continuous integration systems

- **Additional Testing Tools**:
  - **Black 25.1.0**: Uncompromising code formatter for consistent Python styling
  - **Flake8 7.2.0**: Comprehensive linting tool for code quality enforcement
  - **MyPy 1.15.0**: Static type checker for Python code validation
  - **Hypothesis**: Property-based testing library for robust test generation
  - **pytest-asyncio**: Testing support for asynchronous Python code

### Advanced Frontend Technology Stack

**Core Framework and Development Environment**

- **React 18+**: Modern JavaScript library for building interactive user interfaces
  - Component-based architecture with reusable biological data visualization components
  - Virtual DOM for efficient rendering of complex phylogenetic trees
  - Hooks API for state management and side effects in biological analysis workflows
  - Concurrent features for responsive user experiences during long-running analyses
  - Server-side rendering capabilities for improved SEO and performance
  - Error boundaries for graceful handling of visualization errors

- **TypeScript 4.9+**: Statically typed superset of JavaScript
  - Enhanced IDE support with intelligent code completion for biological data structures
  - Compile-time error detection for improved reliability in scientific applications
  - Advanced type system for modeling complex phylogenetic and orthogroup data
  - Generic types for reusable biological data analysis components
  - Integration with scientific computing libraries and type definitions

**Build Tools and Development Infrastructure**

- **Vite 4+**: Next-generation frontend build tool optimized for modern development
  - Lightning-fast cold server start using native ES modules
  - Hot module replacement (HMR) for instant development feedback
  - Optimized build process with Rollup bundling for production
  - Plugin ecosystem for extensible functionality
  - TypeScript support out of the box
  - CSS preprocessing and optimization

**User Interface and Styling Framework**

- **Material-UI (MUI) 5+**: Comprehensive React UI library implementing Material Design
  - Complete component library for rapid scientific application development
  - Theming system for consistent visual design across biological data interfaces
  - Accessibility features built into all components (WCAG 2.1 AA compliance)
  - Responsive design capabilities for multiple device types and screen sizes
  - Customizable design tokens for scientific data visualization themes
  - Integration with popular styling solutions (emotion, styled-components)

**Data Visualization and Scientific Graphics**

- **D3.js 7+**: Powerful data visualization library for complex scientific graphics
  - SVG-based rendering for scalable phylogenetic tree visualizations
  - Interactive data visualization capabilities with zoom, pan, and selection
  - Mathematical utilities optimized for biological data representation
  - Animation support for dynamic phylogenetic tree manipulations
  - Integration with React through custom hooks and components
  - Performance optimizations for large-scale phylogenetic datasets

**State Management and Application Architecture**

- **Redux Toolkit**: Modern Redux implementation for predictable state management
  - Simplified Redux logic with reduced boilerplate code
  - Built-in support for asynchronous operations and API calls
  - DevTools integration for debugging complex biological analysis workflows
  - TypeScript support for type-safe state management
  - RTK Query for efficient API state management
  - Middleware for handling scientific data transformations

**API Communication and Data Fetching**

- **Axios**: Promise-based HTTP client for API communication
  - Request and response interceptors for authentication and error handling
  - Automatic request and response data transformation
  - Built-in support for request cancellation and timeout handling
  - Integration with TypeScript for type-safe API calls
  - Support for file uploads and progress tracking
  - Retry mechanisms for robust API communication

### Development and Deployment Infrastructure

**Environment Management and Reproducibility**

- **Conda**: Cross-platform package manager optimized for scientific computing
  - Reproducible environment creation with exact dependency version specifications
  - Binary package distribution for complex scientific libraries with compiled dependencies
  - Environment isolation preventing conflicts between different projects
  - Integration with Jupyter notebooks for interactive development and analysis
  - Support for multiple programming languages (Python, R, C++, Fortran)
  - Channel management for accessing specialized bioinformatics packages

**Containerization and Orchestration**

- **Docker and Docker Compose**: Containerization platform for consistent deployment
  - Multi-stage builds for optimized production images
  - Container orchestration for complex multi-service architectures
  - Volume management for persistent data storage
  - Network isolation and communication between services
  - Resource limitation and monitoring capabilities
  - Integration with container registries for image distribution

**Version Control and Collaboration**

- **Git**: Distributed version control system with advanced branching strategies
  - Git Flow branching model for collaborative scientific software development
  - Large File Storage (LFS) support for biological datasets
  - Commit message conventions for clear development history
  - Integration with continuous integration and deployment systems
  - Tag-based versioning for scientific software releases
  - Merge conflict resolution for collaborative development

**Code Quality and Documentation**

- **Pre-commit**: Framework for managing git pre-commit hooks
  - Automated code formatting with Black and Prettier
  - Linting and type checking integration before commits
  - Custom hooks for project-specific requirements (scientific data validation)
  - Integration with multiple programming languages and frameworks
  - Consistent code quality enforcement across development team

- **Sphinx**: Documentation generation tool for scientific Python projects
  - Automatic API documentation generation from docstrings
  - Mathematical notation support using MathJax for scientific formulas
  - Multiple output formats (HTML, PDF, LaTeX) for different distribution needs
  - Integration with version control for documentation versioning
  - Cross-referencing capabilities for complex scientific documentation

### Database and Storage Technologies

**Relational Database Management**

- **PostgreSQL 14+**: Advanced open-source relational database system
  - ACID compliance for data integrity in scientific applications
  - Advanced indexing capabilities for large biological datasets
  - JSON and JSONB support for flexible phylogenetic data storage
  - Full-text search capabilities for gene and species annotation data
  - Replication and high availability configurations
  - Custom data types for specialized biological data structures

**Caching and Performance Optimization**

- **Redis 7+**: In-memory data structure store for caching and session management
  - High-performance caching for phylogenetic analysis results
  - Session storage for user authentication and preferences
  - Real-time data streaming capabilities for live analysis updates
  - Cluster support for horizontal scaling
  - Persistence options for data durability
  - Pub/Sub messaging for real-time notifications

**File Storage and Content Delivery**

- **MinIO**: High-performance object storage system compatible with Amazon S3
  - Scalable storage for large phylogenetic datasets and user uploads
  - Version control for biological data files
  - Access control and security policies
  - Integration with content delivery networks (CDN)
  - Backup and disaster recovery capabilities
  - Multi-tenancy support for research group isolation

## Licensing and Legal Considerations

### Comprehensive Open Source License Framework

OrthoViewer operates under the GNU General Public License version 3.0 (GPLv3), a robust copyleft license that ensures the software remains free and open source for the global scientific community. This licensing choice is mandated by the integration of the ETE Toolkit, which is also distributed under GPLv3, creating a legally consistent and compliant licensing framework.

### Detailed License Compatibility Matrix

| Component | Version | License | Compatibility Status | Integration Method | Legal Risk Assessment |
|-----------|---------|---------|---------------------|-------------------|----------------------|
| **OrthoViewer Core** | 1.2.0 | GPLv3 | Primary License | Direct Integration | No Risk |
| **ETE Toolkit** | 3.1.3 | GPLv3 | Full Compatibility | Direct Dependency | No Risk |
| **FastAPI** | 0.95.1 | MIT | GPL Compatible | Dynamic Linking | No Risk |
| **React** | 18+ | MIT | GPL Compatible | Separate Application Layer | No Risk |
| **NumPy** | 1.24.2 | BSD-3-Clause | GPL Compatible | Dynamic Linking | No Risk |
| **Pandas** | 2.0.0 | BSD-3-Clause | GPL Compatible | Dynamic Linking | No Risk |
| **D3.js** | 7+ | BSD-3-Clause | GPL Compatible | Client-side Library | No Risk |
| **Pydantic** | 1.10.22 | MIT | GPL Compatible | Direct Dependency | No Risk |
| **Uvicorn** | 0.22.0 | BSD-3-Clause | GPL Compatible | Dynamic Linking | No Risk |
| **Pytest** | 8.3.5 | MIT | GPL Compatible | Development Tool | No Risk |
| **Material-UI** | 5+ | MIT | GPL Compatible | Client-side Library | No Risk |
| **Redux Toolkit** | 1.9+ | MIT | GPL Compatible | Client-side Library | No Risk |
| **Axios** | 1.4+ | MIT | GPL Compatible | Client-side Library | No Risk |
| **TypeScript** | 4.9+ | Apache 2.0 | GPL Compatible | Development Tool | No Risk |
| **Vite** | 4+ | MIT | GPL Compatible | Build Tool | No Risk |
| **Docker** | 20.10+ | Apache 2.0 | GPL Compatible | Deployment Tool | No Risk |
| **PostgreSQL** | 14+ | PostgreSQL License | GPL Compatible | Database System | No Risk |
| **Redis** | 7+ | BSD-3-Clause | GPL Compatible | Caching System | No Risk |
| **Nginx** | 1.20+ | BSD-2-Clause | GPL Compatible | Web Server | No Risk |

### GNU General Public License v3.0 Implications and Benefits

**Fundamental Freedoms and Rights**

The GPLv3 license provides four essential freedoms that form the foundation of open scientific software:

1. **Freedom 0**: The freedom to run the program for any purpose, including commercial research, academic studies, and educational use
2. **Freedom 1**: The freedom to study how the program works and change it to suit your needs, with access to source code being a precondition
3. **Freedom 2**: The freedom to redistribute copies to help your fellow researchers and institutions
4. **Freedom 3**: The freedom to distribute copies of your modified versions to others, allowing the entire scientific community to benefit from improvements

**Copyleft Requirements and Compliance**

The GPLv3 copyleft mechanism ensures that all derivative works maintain the same freedom guarantees:

- **Source Code Availability**: All derivative works must be distributed under GPLv3 with complete source code
- **Patent Grant Protection**: Automatic patent grants are included for all contributors, protecting users from patent litigation
- **Compatible License Integration**: Software under GPL-compatible licenses may be combined with GPLv3 code
- **Tivoization Prevention**: Hardware manufacturers cannot use technical measures to prevent users from running modified versions

**Scientific Research and Academic Use Considerations**

GPLv3 provides specific advantages for scientific and academic communities:

- **Unrestricted Academic Use**: No limitations on research applications, data analysis, or educational activities
- **Collaborative Development**: Encourages collaborative improvement of scientific software tools
- **Reproducible Research**: Ensures access to complete source code for research reproducibility
- **Commercial Compatibility**: Commercial use is permitted with compliance to copyleft provisions
- **Publication Freedom**: Research results using OrthoViewer may be published without restrictions

### Comprehensive Dependency License Analysis

**Permissive Licenses Compatible with GPLv3**

The majority of OrthoViewer's dependencies use permissive licenses that are fully compatible with GPLv3:

**MIT License Dependencies**
- **Characteristics**: Minimal restrictions with maximum flexibility
- **Patent Clauses**: No explicit patent protection provisions
- **Attribution Requirements**: Copyright notice and license text inclusion required
- **Commercial Use**: Unrestricted commercial applications permitted
- **GPLv3 Compatibility**: Full compatibility through dynamic linking and separate compilation

**BSD-3-Clause License Dependencies**
- **Characteristics**: Similar to MIT with additional non-endorsement clause
- **Patent Disclaimers**: Explicit disclaimers of patent grant provisions
- **Attribution Requirements**: Copyright notice, license text, and contributor acknowledgment
- **Commercial Use**: Unrestricted commercial applications with attribution
- **GPLv3 Compatibility**: Full compatibility with proper attribution maintenance

**Apache License 2.0 Dependencies**
- **Characteristics**: Comprehensive license with explicit patent grant provisions
- **Patent Protection**: Explicit patent grant from contributors to users
- **Trademark Clauses**: Protection of contributor trademarks and names
- **Attribution Requirements**: Detailed attribution and modification documentation
- **GPLv3 Compatibility**: Compatible in most jurisdictions with proper compliance

**Specialized Scientific Software Licenses**

**Python Software Foundation License**
- **Scope**: Python standard library and core runtime components
- **Characteristics**: GPL-compatible license specifically designed for Python ecosystem
- **Academic Use**: Unrestricted use in academic and research environments
- **Commercial Use**: Permitted with proper attribution

**PostgreSQL License**
- **Scope**: PostgreSQL database system and related tools
- **Characteristics**: Very liberal license similar to MIT/BSD
- **Academic Use**: No restrictions on research applications
- **Commercial Use**: Unrestricted commercial deployment

### License Compliance Implementation

**Source Code Distribution Requirements**

OrthoViewer implements comprehensive license compliance through:

1. **Complete Source Availability**: All source code available through public repositories
2. **Build Documentation**: Complete compilation and installation procedures documented
3. **Dependency Tracking**: Comprehensive inventory of all dependencies and their licenses
4. **License Text Inclusion**: All required license texts included in distributions
5. **Attribution Maintenance**: Proper attribution for all incorporated libraries and tools

**Binary Distribution Compliance**

When distributing compiled versions of OrthoViewer:

1. **Source Code Offer**: Written offer to provide complete source code
2. **Build Environment Documentation**: Documentation for reproducible compilation
3. **Dependency Documentation**: Complete list of all included dependencies
4. **License Package**: Comprehensive license documentation package
5. **Version Tracking**: Clear identification of source code versions used

**Research and Publication Guidelines**

**Academic Citation Requirements**

Researchers using OrthoViewer in academic work should:

1. **Software Citation**: Cite OrthoViewer with version number and repository URL
2. **Method Documentation**: Document analysis parameters and procedures used
3. **Reproducibility Information**: Provide sufficient detail for result reproduction
4. **Data Availability**: Follow institutional data sharing policies

**Commercial Use Compliance**

Organizations using OrthoViewer commercially must:

1. **GPL Compliance**: Ensure all copyleft requirements are met
2. **Source Code Availability**: Provide source code to recipients of binary distributions
3. **License Documentation**: Include complete license documentation
4. **Modification Disclosure**: Document any modifications made to the software

### International Legal Considerations

**Multi-Jurisdictional Compliance**

GPLv3 provides consistent legal framework across multiple jurisdictions:

- **United States**: Strong copyright protection with clear fair use provisions
- **European Union**: Compliance with EU copyright law and GDPR data protection
- **International**: Berne Convention compatibility for global copyright protection
- **Academic Institutions**: Compatibility with institutional intellectual property policies

**Export Control and Research Security**

OrthoViewer complies with international research security requirements:

- **Open Source Exception**: Qualifies for open source software export control exceptions
- **Academic Research**: Supports fundamental research classification
- **International Collaboration**: Enables global scientific collaboration
- **Security Best Practices**: Implements security measures without restricting access

This comprehensive licensing framework ensures that OrthoViewer remains freely available to the global scientific community while maintaining legal compliance and protecting the rights of all contributors and users.