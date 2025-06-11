# Hướng dẫn Đóng góp và Mở rộng Dự án

## Mục lục
1. [Cấu trúc Dự án](#cấu-trúc-dự-án)
2. [Quy trình Phát triển](#quy-trình-phát-triển)
3. [Thêm Tính năng Mới](#thêm-tính-năng-mới)
4. [Testing](#testing)
5. [Code Style](#code-style)
6. [Documentation](#documentation)
7. [Deployment](#deployment)

## Cấu trúc Dự án

```
zabbix_mcp/
├── app/
│   ├── api/          # API endpoints
│   ├── core/         # Core functionality
│   ├── models/       # Data models
│   └── services/     # Business logic
├── tests/            # Unit tests
├── scripts/          # Utility scripts
└── logs/            # Log files
```

### Giải thích các thư mục

- **api/**: Chứa các API endpoints
  - Mỗi file tương ứng với một nhóm API
  - Sử dụng FastAPI Router
  - Xử lý request/response

- **core/**: Chứa core functionality
  - Logging
  - Configuration
  - Database connection
  - Cache connection

- **models/**: Chứa data models
  - Pydantic models
  - Database models
  - Request/Response models

- **services/**: Chứa business logic
  - Event analysis
  - Authentication
  - Caching
  - Database operations

## Quy trình Phát triển

1. **Setup môi trường**:
```bash
# Clone repository
git clone https://github.com/thichcode/zabbix_mcp.git
cd zabbix_mcp

# Tạo môi trường ảo
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Cài đặt dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

2. **Tạo branch mới**:
```bash
git checkout -b feature/new-feature
```

3. **Phát triển tính năng**:
- Viết code
- Viết tests
- Chạy tests
- Format code
- Lint code

4. **Commit changes**:
```bash
git add .
git commit -m "feat: add new feature"
```

5. **Push và tạo Pull Request**:
```bash
git push origin feature/new-feature
```

## Thêm Tính năng Mới

### 1. Thêm API Endpoint

```python
# app/api/new_feature.py
from fastapi import APIRouter, Depends
from app.services.auth_service import get_api_key
from app.models.new_model import NewModel

router = APIRouter()

@router.get("/new-feature", dependencies=[Depends(get_api_key)])
async def new_feature():
    return {"message": "New feature"}
```

### 2. Thêm Service

```python
# app/services/new_service.py
from app.core.logging import get_logger
from app.services.database import DatabaseService
from app.services.cache import CacheService

logger = get_logger(__name__)

class NewService:
    def __init__(self, db: DatabaseService, cache: CacheService):
        self.db = db
        self.cache = cache
        self.logger = logger

    async def do_something(self):
        try:
            # Implementation
            pass
        except Exception as e:
            self.logger.error(f"Error in do_something: {str(e)}")
            raise
```

### 3. Thêm Model

```python
# app/models/new_model.py
from pydantic import BaseModel, Field
from datetime import datetime

class NewModel(BaseModel):
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Name of the item")
    created_at: datetime = Field(default_factory=datetime.now)
```

### 4. Thêm Docker Service

```yaml
# docker-compose.yml
services:
  new_service:
    image: new_service_image
    volumes:
      - new_service_data:/data
    networks:
      - zabbix_network
    environment:
      - NEW_SERVICE_CONFIG=value
```

## Testing

### 1. Unit Tests

```python
# tests/test_new_feature.py
import pytest
from app.services.new_service import NewService

@pytest.fixture
def new_service(db_service, cache_service):
    return NewService(db_service, cache_service)

@pytest.mark.asyncio
async def test_new_feature(new_service):
    result = await new_service.do_something()
    assert result is not None
```

### 2. Chạy Tests

```bash
# Chạy tất cả tests
pytest

# Chạy test cụ thể
pytest tests/test_new_feature.py

# Chạy test với coverage
pytest --cov=app tests/
```

## Code Style

### 1. Format Code

```bash
# Format với black
black .

# Sort imports
isort .
```

### 2. Lint Code

```bash
# Lint với flake8
flake8

# Type checking
mypy .
```

## Documentation

### 1. API Documentation

- Sử dụng docstrings
- Mô tả parameters
- Mô tả responses
- Thêm examples

```python
@router.get("/new-feature")
async def new_feature():
    """
    Get new feature information.

    Returns:
        dict: Feature information
    """
    return {"message": "New feature"}
```

### 2. Code Documentation

- Thêm comments cho complex logic
- Mô tả purpose của functions
- Mô tả parameters và return values

## Deployment

### 1. Local Development

```bash
# Chạy với Docker
docker-compose up -d

# Chạy trực tiếp
uvicorn app.main:app --reload
```

### 2. Production

```bash
# Build Docker images
docker-compose build

# Deploy
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Monitoring

- Kiểm tra logs: `docker-compose logs -f app`
- Kiểm tra health: `curl http://localhost:8000/api/v1/health`
- Kiểm tra metrics: Prometheus endpoint (coming soon)

## Best Practices

1. **Code Quality**:
   - Viết tests cho mọi tính năng mới
   - Sử dụng type hints
   - Format code trước khi commit
   - Lint code trước khi commit

2. **Error Handling**:
   - Xử lý tất cả exceptions
   - Log errors đầy đủ
   - Return meaningful error messages

3. **Performance**:
   - Sử dụng caching khi có thể
   - Tối ưu database queries
   - Sử dụng async/await đúng cách

4. **Security**:
   - Validate input
   - Sanitize output
   - Sử dụng environment variables
   - Không hardcode sensitive data

5. **Documentation**:
   - Cập nhật README.md
   - Cập nhật API documentation
   - Thêm comments cho complex logic

## Liên hệ

Nếu bạn có câu hỏi hoặc cần hỗ trợ, vui lòng:
1. Tạo issue trên GitHub
2. Liên hệ qua email
3. Tham gia discussion trên GitHub 