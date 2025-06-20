-----

# Zabbix MCP Server

MCP (Monitoring Control Panel) Server is an intelligent analysis system for Zabbix that automatically analyzes and processes triggers from Zabbix.

## Main Features

### 1\. Trigger Analysis

  * Root Cause Analysis (RCA)
  * Trend and pattern analysis
  * Impact and influence analysis
  * Automatic solution recommendations

### 2\. Trend Analysis

  * Analysis of trigger occurrence frequency
  * Analysis of severity levels over time
  * Analysis of recovery time
  * Prediction of future trends

### 3\. Impact Analysis

  * Direct impact analysis
  * Indirect impact analysis
  * Impact analysis over time
  * Business cost estimation

### 4\. Security

  * API key authentication
  * Rate limiting (60 requests/minute)
  * Detailed logging
  * System health check

## Installation

### Requirements

  * Python 3.8+
  * MongoDB 4.4+
  * Redis 6.0+
  * Zabbix 5.0+

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configuration

1.  Create a `.env` file with the following environment variables:

<!-- end list -->

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

2.  Configure Zabbix webhook:

<!-- end list -->

```bash
python scripts/setup_zabbix.py
```

### Run with Docker

```bash
docker-compose up -d
```

## API Endpoints

### Webhook

```
POST /api/v1/webhook/zabbix
```

Receives and analyzes triggers from Zabbix.

Headers:

  * `X-API-Key`: API key for authentication

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

Checks the status of the services.

## Project Structure

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

## Analysis

### Trend Analysis

  * Frequency of trigger occurrences
  * Severity level over time
  * Average recovery time
  * Trend prediction

### Impact Analysis

  * Direct impact
      * Severity level
      * Affected host
      * Affected item
      * Required actions
  * Indirect impact
      * Affected services
      * Affected users
      * Chain effect
      * Business impact
  * Impact over time
      * Time of occurrence
      * Recovery time
      * Historical patterns

## Security

### Authentication

  * API key required for webhook
  * Source IP check
  * Rate limiting

### Logging

  * Log all requests
  * Log analysis results
  * Log errors and warnings

## Monitoring

### Health Check

  * Check MongoDB
  * Check Redis
  * Check Zabbix API
  * Check AI service

### Metrics

  * Number of triggers
  * Analysis time
  * Analysis accuracy
  * Recovery rate

## Contributing

See [CONTRIBUTING.md](https://www.google.com/search?q=CONTRIBUTING.md) for more details.

## License

MIT License
