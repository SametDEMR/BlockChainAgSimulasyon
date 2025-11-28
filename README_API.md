# Blockchain Attack Simulator - API

## Kurulum

```bash
pip install -r requirements.txt
```

## API Sunucusu Başlatma

```bash
python backend/main.py
```

API şu adreste çalışır: `http://localhost:8000`

## API Endpoints

### Health Check
```
GET /
```

### Status
```
GET /status
```
Simülatör durumunu döndürür.

### Blockchain
```
GET /blockchain
```
İlk node'un blockchain'ini döndürür.

### Nodes
```
GET /nodes
GET /nodes/{node_id}
```
Tüm node'ları veya belirli bir node'u döndürür.

### Control
```
POST /start      - Simülasyonu başlat
POST /stop       - Simülasyonu durdur
POST /reset      - Simülasyonu sıfırla
```

## Test

API'yi test etmek için (API sunucusu çalışırken):
```bash
python test_api.py
```

## API Dokümantasyonu

Swagger UI: `http://localhost:8000/docs`
ReDoc: `http://localhost:8000/redoc`
