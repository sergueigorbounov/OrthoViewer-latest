# 🧬 OrthoViewer2 Backend Architecture

## 📐 3-Layer Architecture

### 🎯 Design Principles
- **Separation of Concerns**: Clear boundaries between layers
- **Dependency Inversion**: Higher layers depend on abstractions, not concrete implementations
- **Single Responsibility**: Each layer has one primary responsibility
- **Testability**: Each layer can be tested independently

## 🏗️ Layer Structure

```
backend/
├── app/
│   ├── api/                    # 🌐 API LAYER
│   │   ├── routes/            # HTTP route handlers
│   │   ├── middleware/        # Request/response middleware
│   │   └── dependencies/      # FastAPI dependencies
│   ├── services/              # ⚙️ SERVICE LAYER  
│   │   ├── biological/        # Core business logic
│   │   ├── analysis/          # Data analysis services
│   │   └── visualization/     # Visualization services
│   ├── repositories/          # 💾 DATA ACCESS LAYER
│   │   ├── file/              # File-based data access
│   │   ├── database/          # Database repositories
│   │   └── cache/             # Caching layer
│   └── models/                # 📋 SHARED MODELS
│       ├── domain/            # Business domain models
│       ├── dto/               # Data transfer objects
│       └── entities/          # Database entities
└── tests/
    ├── unit/                  # 🧪 Unit tests by layer
    │   ├── api/
    │   ├── services/
    │   └── repositories/
    ├── integration/           # 🔗 Integration tests
    └── performance/           # ⚡ Performance tests
```

## 📋 Layer Responsibilities

### 🌐 API Layer (`app/api/`)
**Purpose**: HTTP interface and request handling

**Responsibilities**:
- HTTP request/response handling
- Input validation and serialization
- Authentication and authorization
- Route parameter binding
- Error handling and status codes

**Files**:
- `routes/`: FastAPI route handlers
- `middleware/`: Custom middleware
- `dependencies/`: Dependency injection

**Testing**: Focus on HTTP contracts, status codes, serialization

### ⚙️ Service Layer (`app/services/`)
**Purpose**: Business logic and orchestration

**Responsibilities**:
- Business rule implementation
- Cross-cutting concerns (logging, caching)
- Transaction management
- Service orchestration
- Data transformation

**Files**:
- `biological/`: Core biological data services
- `analysis/`: Data analysis and computation
- `visualization/`: Chart and graph generation

**Testing**: Business logic, edge cases, service integration

### 💾 Data Access Layer (`app/repositories/`)
**Purpose**: Data persistence and retrieval

**Responsibilities**:
- Data access abstractions
- File I/O operations
- Database queries
- Caching implementation
- Data mapping

**Files**:
- `file/`: CSV, JSON file handlers
- `database/`: SQL database access
- `cache/`: Redis or in-memory cache

**Testing**: Data access patterns, file operations, queries

## 🔄 Data Flow

```
HTTP Request → API Layer → Service Layer → Repository Layer → Data Source
                    ↓           ↓              ↓
              Validation → Business Logic → Data Access
                    ↓           ↓              ↓
HTTP Response ← Response DTO ← Domain Model ← Raw Data
```

## ⚡ Performance Requirements

| Operation | Target | Layer |
|-----------|--------|--------|
| Gene search | < 50ms | Service + Repository |
| Species lookup | < 10ms | Repository + Cache |
| Orthogroup retrieval | < 100ms | Service + Repository |
| Dashboard load | < 200ms | Service orchestration |

## 🧪 Testing Strategy

### Unit Tests
- **API Layer**: Mock services, test HTTP contracts
- **Service Layer**: Mock repositories, test business logic
- **Repository Layer**: Test data access patterns

### Integration Tests
- Full stack testing
- Database integration
- File system integration

### Performance Tests
- Load testing
- Response time validation
- Memory usage monitoring

## 🚀 Implementation Guidelines

### API Layer Best Practices
```python
# ✅ Good: Thin controllers
@router.get("/species/{species_id}")
async def get_species(species_id: str, service: SpeciesService = Depends()):
    return await service.get_species_by_id(species_id)

# ❌ Bad: Business logic in controllers
@router.get("/species/{species_id}")
async def get_species(species_id: str):
    # Don't put business logic here
    data = read_csv_file(...)
    processed = complex_calculation(data)
    return processed
```

### Service Layer Best Practices
```python
# ✅ Good: Pure business logic
class SpeciesService:
    def __init__(self, repo: SpeciesRepository):
        self.repo = repo
    
    async def get_species_stats(self, species_id: str) -> SpeciesStats:
        species = await self.repo.get_by_id(species_id)
        return self._calculate_stats(species)
```

### Repository Layer Best Practices
```python
# ✅ Good: Abstract data access
class SpeciesRepository(ABC):
    @abstractmethod
    async def get_by_id(self, species_id: str) -> Species:
        pass

class FileSpeciesRepository(SpeciesRepository):
    async def get_by_id(self, species_id: str) -> Species:
        # File-specific implementation
        pass
```

## 🔧 Dependency Injection

Use FastAPI's dependency system to inject services:

```python
# dependencies.py
def get_species_service() -> SpeciesService:
    repo = FileSpeciesRepository()
    return SpeciesService(repo)

# routes/species.py
@router.get("/species/{species_id}")
async def get_species(
    species_id: str,
    service: SpeciesService = Depends(get_species_service)
):
    return await service.get_species_by_id(species_id)
```

## 📈 Monitoring and Observability

- **Logging**: Structured logging at each layer
- **Metrics**: Performance metrics per layer
- **Tracing**: Request tracing across layers
- **Health Checks**: Layer-specific health endpoints 