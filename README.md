# Zabbix MCP Server

Zabbix MCP Server là một dịch vụ trung gian sử dụng Model Context Protocol để phân tích và tự động xử lý sự kiện Zabbix bằng AI.

## Cấu trúc dự án

```
zabbixmcp/
├── app/
│   ├── api/            # API endpoints
│   ├── core/           # Core logic
│   ├── models/         # Data models
│   └── services/       # Business services
├── config/             # Configuration files
├── scripts/            # Utility scripts
└── tests/              # Test files
```

## Cài đặt

1. Tạo môi trường ảo:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Cấu hình biến môi trường:
- Tạo file `.env` từ mẫu dưới đây
- Điền các thông tin cấu hình cần thiết

### Mẫu file .env
```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=zabbixmcp

# OpenAI Configuration (Sử dụng khi USE_OLLAMA=false)
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4-turbo-preview

# Ollama Configuration (Sử dụng khi USE_OLLAMA=true)
USE_OLLAMA=false
OLLAMA_API_URL=http://localhost:11434
OLLAMA_MODEL=llama2

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Zabbix Configuration
ZABBIX_API_URL=http://localhost/zabbix/api_jsonrpc.php
ZABBIX_USER=Admin
ZABBIX_PASSWORD=zabbix

# n8n Configuration
N8N_WEBHOOK_URL=http://localhost:5678/webhook/zabbix
```

## Chạy server

```bash
uvicorn app.main:app --reload
```

## API Endpoints

- POST `/api/v1/webhook/zabbix`: Webhook endpoint cho Zabbix
- GET `/api/v1/events`: Lấy danh sách sự kiện
- GET `/api/v1/events/{event_id}`: Lấy chi tiết sự kiện
- POST `/api/v1/events/{event_id}/analyze`: Phân tích sự kiện bằng AI

## Tích hợp

### Zabbix
1. Cấu hình External Script trong Zabbix để gửi alert tới webhook
2. Cấu hình n8n để xử lý các hành động tự động

### MongoDB
- Lưu trữ lịch sử RCA và các phân tích
- Tra cứu các sự kiện tương tự

### OpenAI/Ollama
- Phân tích nguyên nhân gốc rễ (RCA)
- Tạo báo cáo tự động

## Cấu hình AI Model

### Sử dụng OpenAI
1. Đặt `USE_OLLAMA=false` trong file `.env`
2. Cung cấp `OPENAI_API_KEY` hợp lệ
3. Chọn model phù hợp trong `OPENAI_MODEL`

### Sử dụng Ollama (Local)
1. Cài đặt Ollama từ https://ollama.ai/
2. Tải model mong muốn:
```bash
ollama pull llama2  # hoặc model khác
```
3. Đặt `USE_OLLAMA=true` trong file `.env`
4. Cấu hình `OLLAMA_API_URL` và `OLLAMA_MODEL`
5. Khởi động Ollama server:
```bash
ollama serve
``` 