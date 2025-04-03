# MLOps Assignment - System Monitoring Solution

## Components
1. Custom Python metrics exporter
2. Prometheus metrics collector
3. Grafana dashboard

## Setup Instructions

### Prerequisites
- Docker Desktop (Windows)
- Python 3.9+
- PowerShell

### 1. Start Monitoring Stack
```


# Clean up existing containers

docker rm -f prometheus grafana

# Start services

docker-compose up -d

```

### 2. Run Custom Exporter
```

cd exporter
pip install -r requirements.txt
python prometheus_exporter.py

```

### 3. Access Services
| Service    | URL               |
|------------|-------------------|
| Prometheus | http://localhost:9090 |
| Grafana    | http://localhost:3000 |

### 4. Grafana Configuration
1. Login with admin/admin.
2. Add Prometheus data source: `http://prometheus:9090`.
3. Import dashboard ID `1860` for Node Exporter metrics.

## Validation Tests
1. Check exporter metrics:
```

http://localhost:18000/metrics

```
2. Verify Prometheus targets: Status &gt; Targets.

![alt text](image.png)