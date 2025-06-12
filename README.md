# Zabbix MCP Server

MCP (Monitoring Control Panel) Server là một hệ thống phân tích thông minh cho Zabbix, giúp tự động phân tích và xử lý các trigger từ Zabbix.

## Tính năng chính

### 1. Phân tích Trigger
- Phân tích nguyên nhân gốc rễ (RCA)
- Phân tích xu hướng và mẫu
- Phân tích tác động và ảnh hưởng
- Đề xuất giải pháp tự động

### 2. Phân tích Xu hướng
- Phân tích tần suất xuất hiện của trigger
- Phân tích mức độ nghiêm trọng theo thời gian
- Phân tích thời gian phục hồi
- Dự đoán xu hướng trong tương lai

### 3. Phân tích Tác động
- Phân tích tác động trực tiếp
- Phân tích tác động gián tiếp
- Phân tích tác động theo thời gian
- Ước tính chi phí kinh doanh

### 4. Bảo mật
- Xác thực API key
- Rate limiting (60 request/phút)
- Logging chi tiết
- Kiểm tra sức khỏe hệ thống

## Cài đặt

### Yêu cầu
- Python 3.8+
- MongoDB 4.4+
- Redis 6.0+
- Zabbix 5.0+

### Cài đặt dependencies
```bash
pip install -r requirements.txt
```

### Cấu hình
1. Tạo file `.env` với các biến môi trường:
```env
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=zabbix_mcp
REDIS_HOST=localhost
REDIS_PORT=6379
ZABBIX_API_URL=http://your-zabbix-server/api_jsonrpc.php
ZABBIX_USER=Admin
ZABBIX_PASSWORD=zabbix
ZABBIX_WEBHOOK_API_KEY=your-secret-key
OPENAI_API_KEY=your-openai-key
USE_OLLAMA=false
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=llama2
```

2. Cấu hình Zabbix webhook:
```bash
python scripts/setup_zabbix.py
```

### Chạy với Docker
```bash
docker-compose up -d
```

## API Endpoints

### Webhook
```
POST /api/v1/webhook/zabbix
```
Nhận trigger từ Zabbix và phân tích.

Headers:
- `X-API-Key`: API key để xác thực

Body:
```json
{
    "event": {
        "event_id": "string",
        "host": "string",
        "item": "string",
        "trigger": "string",
        "severity": "integer",
        "status": "string",
        "timestamp": "datetime",
        "value": "string",
        "description": "string",
        "tags": []
    },
    "action": "string"
}
```

### Health Check
```
GET /api/v1/health
```
Kiểm tra trạng thái của các service.

## Cấu trúc dự án

```
zabbixmcp/
├── app/
│   ├── api/
│   │   ├── webhook.py
│   │   └── health.py
│   ├── models/
│   │   └── event.py
│   ├── services/
│   │   ├── analysis.py
│   │   ├── database.py
│   │   ├── trend_analysis.py
│   │   ├── impact_analysis.py
│   │   ├── deep_research.py
│   │   ├── rag_service.py
│   │   └── ollama_service.py
│   └── core/
│       └── logging.py
├── config/
├── scripts/
│   └── setup_zabbix.py
├── tests/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## Phân tích

### Phân tích Xu hướng
- Tần suất xuất hiện của trigger
- Mức độ nghiêm trọng theo thời gian
- Thời gian phục hồi trung bình
- Dự đoán xu hướng

### Phân tích Tác động
- Tác động trực tiếp
  - Mức độ nghiêm trọng
  - Host bị ảnh hưởng
  - Item bị ảnh hưởng
  - Hành động cần thiết
- Tác động gián tiếp
  - Service bị ảnh hưởng
  - User bị ảnh hưởng
  - Hiệu ứng dây chuyền
  - Tác động kinh doanh
- Tác động theo thời gian
  - Thời điểm xảy ra
  - Thời gian phục hồi
  - Mẫu lịch sử

## Bảo mật

### Xác thực
- API key bắt buộc cho webhook
- Kiểm tra IP nguồn
- Rate limiting

### Logging
- Log tất cả request
- Log kết quả phân tích
- Log lỗi và cảnh báo

## Monitoring

### Health Check
- Kiểm tra MongoDB
- Kiểm tra Redis
- Kiểm tra Zabbix API
- Kiểm tra AI service

### Metrics
- Số lượng trigger
- Thời gian phân tích
- Độ chính xác của phân tích
- Tỷ lệ phục hồi

## Contributing

Xem [CONTRIBUTING.md](CONTRIBUTING.md) để biết thêm chi tiết.

## License

MIT License 