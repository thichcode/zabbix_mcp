# Zabbix MCP Server

Middleware service sử dụng Model Context Protocol để phân tích và tự động hóa các sự kiện Zabbix với AI.

## Tính năng

- Phân tích sự kiện Zabbix bằng AI (OpenAI/Ollama)
- Tự động hóa phản hồi sự cố
- Tích hợp với n8n cho workflow automation
- Caching và Rate Limiting
- Health Check System
- Logging System
- Unit Tests
- API Documentation

## Yêu cầu hệ thống

### Cài đặt bằng Docker
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM trở lên
- 20GB ổ cứng trống

## Cài đặt

### Cài đặt bằng Docker (Khuyến nghị)

1. Clone repository:
```bash
git clone https://github.com/thichcode/zabbix_mcp.git
cd zabbix_mcp
```

2. Cấu hình môi trường:
```bash
cp .env.example .env
# Chỉnh sửa file .env với cấu hình của bạn
```

3. Build và chạy containers:
```bash
docker-compose up -d
```

4. Kiểm tra logs:
```bash
docker-compose logs -f app
```

5. Kiểm tra health:
```bash
curl http://localhost:8000/api/v1/health
```

### Cài đặt thủ công

1. Clone repository:
```bash
git clone https://github.com/thichcode/zabbix_mcp.git
cd zabbix_mcp
```

2. Tạo và kích hoạt môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

4. Cấu hình môi trường:
```bash
cp .env.example .env
# Chỉnh sửa file .env với cấu hình của bạn
```

5. Cài đặt và cấu hình MongoDB:
```bash
# Ubuntu/Debian
sudo apt-get install mongodb
sudo systemctl start mongodb

# Windows
# Tải và cài đặt từ https://www.mongodb.com/try/download/community
```

6. Cài đặt và cấu hình Redis:
```bash
# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server

# Windows
# Tải từ https://github.com/microsoftarchive/redis/releases
```

7. Cấu hình Zabbix:
```bash
# Chạy script cấu hình
python scripts/setup_zabbix.py
```

## Chạy ứng dụng

### Docker
```bash
# Khởi động
docker-compose up -d

# Dừng
docker-compose down

# Xem logs
docker-compose logs -f app

# Restart
docker-compose restart app
```

### Thủ công
1. Chạy tests:
```bash
pytest tests/
```

2. Chạy server:
```bash
uvicorn app.main:app --reload
```

3. Kiểm tra health:
```bash
curl http://localhost:8000/api/v1/health
```

4. Xem logs:
```bash
tail -f logs/api_*.log
```

## Cấu hình Docker

### Volumes
- `mongodb_data`: Lưu trữ dữ liệu MongoDB
- `redis_data`: Lưu trữ dữ liệu Redis
- `ollama_data`: Lưu trữ models Ollama
- `./logs`: Log files
- `./.env`: Environment variables

### Networks
- `zabbix_network`: Network cho các services

### Ports
- `8000`: API server
- `27017`: MongoDB
- `6379`: Redis
- `11434`: Ollama (tùy chọn)

## API Endpoints

- `GET /api/v1/health`: Kiểm tra trạng thái hệ thống
- `POST /api/v1/webhook`: Webhook endpoint cho Zabbix
- `GET /docs`: API documentation (Swagger UI)

## Cấu trúc dự án

```
zabbix_mcp/
├── app/
│   ├── api/
│   │   ├── webhook.py
│   │   └── health.py
│   ├── core/
│   │   └── logging.py
│   ├── models/
│   │   └── event.py
│   ├── services/
│   │   ├── analysis.py
│   │   ├── auth_service.py
│   │   ├── cache_service.py
│   │   ├── database.py
│   │   ├── deep_research.py
│   │   └── ollama_service.py
│   └── main.py
├── tests/
│   └── test_analysis.py
├── scripts/
│   └── setup_zabbix.py
├── logs/
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── README.md
└── requirements.txt
```

## Monitoring

- Health Check: `/api/v1/health`
- Logs: `logs/` directory hoặc `docker-compose logs`
- Metrics: Prometheus metrics (coming soon)

## Development

1. Cài đặt development dependencies:
```bash
pip install -r requirements-dev.txt
```

2. Chạy code formatting:
```bash
black .
isort .
```

3. Chạy linting:
```bash
flake8
mypy .
```

4. Chạy tests với coverage:
```bash
pytest --cov=app tests/
```

## Contributing

1. Fork repository
2. Tạo branch mới
3. Commit changes
4. Push lên branch
5. Tạo Pull Request

## License

MIT License 