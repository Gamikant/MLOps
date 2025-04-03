from prometheus_client import start_http_server, Gauge
import psutil
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Disk Metrics
io_read_rate = Gauge('io_read_rate', 'Read ops/sec', ['device'])
io_write_rate = Gauge('io_write_rate', 'Write ops/sec', ['device'])
io_tps = Gauge('io_tps', 'Transfers/sec', ['device'])

# Memory Metrics
mem_metrics = {
    'available': Gauge('meminfo_available', 'Available memory'),
    'used': Gauge('meminfo_used', 'Used memory'),
    'free': Gauge('meminfo_free', 'Free memory')
}

# CPU Metrics
cpu_usage = Gauge('cpu_usage', 'CPU utilization', ['core'])

def collect_disk_metrics():
    for disk, stats in psutil.disk_io_counters(perdisk=True).items():
        io_read_rate.labels(disk).set(stats.read_count)
        io_write_rate.labels(disk).set(stats.write_count)
        io_tps.labels(disk).set(stats.read_count + stats.write_count)

def collect_memory_metrics():
    mem = psutil.virtual_memory()
    mem_metrics['available'].set(mem.available)
    mem_metrics['used'].set(mem.used)
    mem_metrics['free'].set(mem.free)

def collect_cpu_metrics():
    for core, percent in enumerate(psutil.cpu_percent(percpu=True)):
        cpu_usage.labels(core).set(percent)

if __name__ == '__main__':
    start_http_server(18000)
    while True:
        collect_disk_metrics()
        collect_memory_metrics()
        collect_cpu_metrics()
        time.sleep(1)
