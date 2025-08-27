import json
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from datetime import datetime
from pathlib import Path

def get_datetime():
    return datetime.now().isoformat()

def get_uptime():
    try:
        with open("/proc/uptime") as f:
            return int(float(f.readline().split()[0]))
    except:
        return 0

def read_proc_stat():
    with open("/proc/stat") as f:
        parts = list(map(int, f.readline().split()[1:]))
        total = sum(parts)
        idle = parts[3] + parts[4]
        return total, idle

def get_cpu_info():
    model, speed, usage = "Unknown", 0.0, 0.0
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    model = line.split(":")[1].strip()
                elif line.startswith("cpu MHz"):
                    speed = float(line.split(":")[1].strip())
    except:
        pass

    try:
        t1, idle1 = read_proc_stat()
        time.sleep(0.1)
        t2, idle2 = read_proc_stat()
        dt, didle = t2 - t1, idle2 - idle1
        usage = 100.0 * (dt - didle) / dt if dt > 0 else 0.0
    except:
        pass

    return {"model": model, "speed_mhz": speed, "usage_percent": round(usage, 2)}

def get_memory_info():
    total, free = 0, 0
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal:"):
                    total = int(line.split()[1]) // 1024
                elif line.startswith("MemAvailable:"):
                    free = int(line.split()[1]) // 1024
    except:
        pass
    return {"total_mb": total, "used_mb": total - free}

def get_os_version():
    try:
        with open("/proc/version") as f:
            return f.readline().strip()
    except:
        return "Unknown"

def get_process_list():
    procs = []
    for entry in Path("/proc").iterdir():
        if entry.is_dir() and entry.name.isdigit():
            try:
                with open(entry / "comm") as f:
                    name = f.readline().strip()
                procs.append({"pid": int(entry.name), "name": name})
            except:
                continue
    return procs

def get_disks():
    disks = []
    sys_block = Path("/sys/block")
    if sys_block.exists():
        for dev in sys_block.iterdir():
            size_file = dev / "size"
            if size_file.exists():
                try:
                    with open(size_file) as f:
                        sectors = int(f.readline().strip())
                        size_mb = (sectors * 512) // (1024 * 1024)
                        disks.append({"device": dev.name, "size_mb": size_mb})
                except:
                    continue
    return disks

def get_usb_devices():
    devices = []
    usb_sys = Path("/sys/bus/usb/devices")
    if usb_sys.exists():
        for dev in usb_sys.iterdir():
            product_file = dev / "product"
            if product_file.exists():
                try:
                    with open(product_file) as f:
                        desc = f.readline().strip()
                    devices.append({"port": dev.name, "description": desc})
                except:
                    continue
    return devices

def get_network_adapters():
    adapters = []
    sys_net = Path("/sys/class/net")
    if sys_net.exists():
        for iface in sys_net.iterdir():
            ifname = iface.name
            if ifname == "lo":
                continue
            ip_addr = None
            try:
                with open("/proc/net/fib_trie") as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines):
                        if f"dev {ifname}" in line:
                            for j in range(i, len(lines)):
                                if "32 host" in lines[j]:
                                    ip_addr = lines[j].split()[1]
                                    break
                            if ip_addr:
                                break
            except:
                pass
            adapters.append({"interface": ifname, "ip_address": ip_addr})
    return adapters


class StatusHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/status":
            self.send_response(404)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"error": "Bad Request"}')
            return

        response = {
            "datetime": get_datetime(),
            "uptime_seconds": get_uptime(),
            "cpu": get_cpu_info(),
            "memory": get_memory_info(),
            "os_version": get_os_version(),
            "processes": get_process_list(),
            "disks": get_disks(),
            "usb_devices": get_usb_devices(),
            "network_adapters": get_network_adapters()
        }

        data = json.dumps(response, indent=2).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

def run_server(port=8080):
    print(f"Servidor disponível em http://0.0.0.0:{port}/status")
    server = HTTPServer(("0.0.0.0", port), StatusHandler)
    server.serve_forever()

if __name__ == "__main__":
    run_server()
