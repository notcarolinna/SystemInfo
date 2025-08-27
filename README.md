# SystemInfo: Servidor HTTP para Exportação de Informações do Sistema

## Descrição

O **SystemInfo** é um servidor HTTP que fornece informações detalhadas do sistema Linux através do endpoint `/status`. Ao acessar este endpoint, o usuário recebe dados como:

* Uso de CPU
* Memória disponível e usada
* Informações do kernel e versão do SO
* Tempo de atividade do sistema
* Lista de processos ativos
* Dispositivos de armazenamento e USB
* Interfaces de rede

As informações são coletadas diretamente dos arquivos do sistema localizados em `/proc` e `/sys`, fontes primárias de dados do Linux.

---

## Resposta do Endpoint `/status`

```json
# cat status
{
  "datetime": "2025-08-27T22:11:53.256305",
  "uptime_seconds": 599,
  "cpu": {
    "model": "QEMU Virtual CPU version 2.5+",
    "speed_mhz": 3194.785,
    "usage_percent": 54.55
  },
  "memory": {
    "total_mb": 116,
    "used_mb": 15
  },
  "os_version": "Linux version 5.15.18 (skad@skad) (i686-buildroot-linux-gnu-,
  "processes": [
    {
      "pid": 1,
      "name": "init"
    },
    {
      "pid": 2,
      "name": "kthreadd"
    },
    {
      "pid": 3,
      "name": "rcu_gp"
    },
    {
      "pid": 4,
      "name": "rcu_par_gp"
    },
    {
      "pid": 6,
      "name": "kworker/0:0H-events_highpri"
    },
    {
      "pid": 7,
      "name": "kworker/u2:0-events_unbound"
    },
    {
      "pid": 8,
      "name": "mm_percpu_wq"
    },
    {
      "pid": 9,
      "name": "ksoftirqd/0"
    },
    {
      "pid": 10,
      "name": "rcu_sched"
    },
    {
      "pid": 11,
      "name": "migration/0"
    },
    {
      "pid": 12,
      "name": "cpuhp/0"
    },
    {
      "pid": 13,
      "name": "kdevtmpfs"
    },
    {
      "pid": 14,
      "name": "netns"
    },
    {
      "pid": 15,
      "name": "inet_frag_wq"
    },
    {
      "pid": 16,
      "name": "oom_reaper"
    },
    {
      "pid": 17,
      "name": "writeback"
    },
    {
      "pid": 18,
      "name": "kcompactd0"
    },
    {
      "pid": 19,
      "name": "kblockd"
    },
    {
      "pid": 20,
      "name": "kworker/0:1-mm_percpu_wq"
    },
    {
      "pid": 21,
      "name": "ata_sff"
    },
    {
      "pid": 22,
      "name": "kswapd0"
    },
    {
      "pid": 23,
      "name": "kworker/0:1H-kblockd"
    },
    {
      "pid": 24,
      "name": "acpi_thermal_pm"
    },
    {
      "pid": 26,
      "name": "scsi_eh_0"
    },
    {
      "pid": 27,
      "name": "scsi_tmf_0"
    },
    {
      "pid": 28,
      "name": "scsi_eh_1"
    },
    {
      "pid": 29,
      "name": "scsi_tmf_1"
    },
    {
      "pid": 31,
      "name": "kworker/u2:3-events_unbound"
    },
    {
      "pid": 32,
      "name": "mld"
    },
    {
      "pid": 33,
      "name": "ipv6_addrconf"
    },
    {
      "pid": 34,
      "name": "kworker/0:2-events"
    },
    {
      "pid": 35,
      "name": "ext4-rsv-conver"
    },
    {
      "pid": 52,
      "name": "syslogd"
    },
    {
      "pid": 56,
      "name": "klogd"
    },
    {
      "pid": 91,
      "name": "udhcpc"
    },
    {
      "pid": 95,
      "name": "python3"
    },
    {
      "pid": 96,
      "name": "sh"
    },
    {
      "pid": 97,
      "name": "getty"
    },
    {
      "pid": 190,
      "name": "wget"
    }
  ],
  "disks": [
    {
      "device": "sda",
      "size_mb": 60
    }
  ],
  "usb_devices": [],
  "network_adapters": [
    {
      "interface": "sit0",
      "ip_address": null
    },
    {
      "interface": "eth0",
      "ip_address": null
    }
  ]
}# 

```

<img width="958" height="143" alt="image" src="https://github.com/user-attachments/assets/e50fcbe7-87da-48a1-91af-75bfe758a5b2" />


---

## Campos do `/status` e como são obtidos

| Campo               | Descrição                     | Fonte                                                       |
| ------------------- | ----------------------------- | ----------------------------------------------------------- |
| `datetime`          | Data e hora atual do sistema  | `datetime.now().isoformat()`                                |
| `uptime_seconds`    | Tempo desde o último boot (s) | `/proc/uptime` (primeiro valor)                             |
| `cpu.model`         | Nome do processador           | `/proc/cpuinfo`, linha "model name"                         |
| `cpu.speed_mhz`     | Frequência em MHz             | `/proc/cpuinfo`, linha "cpu MHz"                            |
| `cpu.usage_percent` | Percentual de uso da CPU      | `/proc/stat` (diferença de tempos em 0.1s)                  |
| `memory.total_mb`   | Memória total em MB           | `/proc/meminfo`, "MemTotal"                                 |
| `memory.used_mb`    | Memória usada em MB           | `MemTotal - MemAvailable`                                   |
| `os_version`        | Versão do sistema operacional | `/proc/version`                                             |
| `processes`         | Lista de processos ativos     | Diretórios numéricos em `/proc`, lendo `comm`               |
| `disks`             | Dispositivos de armazenamento | `/sys/block`, lendo `size` e convertendo setores em MB      |
| `usb_devices`       | Dispositivos USB conectados   | `/sys/bus/usb/devices`, lendo `product`                     |
| `network_adapters`  | Interfaces de rede com IP     | `/sys/class/net` (ignora `lo`), IP via `/proc/net/fib_trie` |

---
