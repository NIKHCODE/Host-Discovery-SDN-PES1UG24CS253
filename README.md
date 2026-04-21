# 🌐 Host Discovery Service — SDN Project

> Automatically detect and maintain a list of hosts in an SDN network using POX Controller and Mininet.

***

## 📋 Problem Statement

In traditional networks, there is no automatic mechanism to know which hosts are connected, on which port, or with which IP. This project solves that using SDN — every time a new host sends its first packet, the controller detects it via `packet_in`, logs it, and maintains a live host database.

***

## 🎯 Objectives

- ✅ Detect host join events via `packet_in` (TABLE MISS)
- ✅ Maintain a dynamic host database (MAC, IP, Switch DPID, Port)
- ✅ Install explicit match-action flow rules reactively
- ✅ Display `NEW HOST DETECTED` in real-time
- ✅ Detect host movement across ports

***

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           APPLICATION LAYER             │
│         host_discovery.py               │  ← Your custom POX module
├─────────────────────────────────────────┤
│            CONTROL LAYER                │
│    POX Controller (OpenFlow 1.0)        │  ← Centralized control plane
│    forwarding.l2_learning               │  ← Built-in L2 learning switch
├─────────────────────────────────────────┤
│         INFRASTRUCTURE LAYER            │
│    Open vSwitch (s1) via OpenFlow       │  ← Data plane forwarding
└─────────────────────────────────────────┘
         ↑ Southbound API: OpenFlow 1.0 / TCP 6633
```

***

## 🔗 Network Topology

```
         POX Controller (c0)
               │
               │ OpenFlow / TCP 6633
               │
          ┌────┴────┐
          │   s1    │  ← OVS Switch (DPID: 1)
          └┬──┬──┬──┬┘
           │  │  │  │
          h1  h2  h3  h4
       port 1  2   3   4
```

| Host | IP Address | MAC Address       | Port on s1 |
|------|------------|-------------------|------------|
| h1   | 10.0.0.1   | 00:00:00:00:00:01 | 1          |
| h2   | 10.0.0.2   | 00:00:00:00:00:02 | 2          |
| h3   | 10.0.0.3   | 00:00:00:00:00:03 | 3          |
| h4   | 10.0.0.4   | 00:00:00:00:00:04 | 4          |

***

## ⚙️ How It Works

```
Host sends first packet
        │
        ▼
Switch: no flow rule → TABLE MISS
        │
        ▼
Switch sends packet_in ──► POX Controller
                                │
                    ┌───────────▼────────────┐
                    │  Extract from packet:  │
                    │  • Source MAC (L2)     │
                    │  • Source IP  (L3)     │
                    │  • Switch DPID         │
                    │  • Ingress Port        │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  New MAC?              │
                    │  → Print NEW HOST      │
                    │  → Store in host_db    │
                    │  Already known?        │
                    │  → Check port change   │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  Install Flow Rule     │
                    │  match: dl_dst = MAC   │
                    │  action: output→port   │
                    │  idle_timeout: 30s     │
                    └────────────────────────┘
                                │
                                ▼
              Future packets forwarded by switch directly
              (no controller involvement = lower latency)
```

***

## 🚀 Setup & Running

### Prerequisites

- Arch Linux / Ubuntu
- Python 3.x
- POX Controller (gar branch) at `~/pox/`
- Mininet 2.3+
- Open vSwitch (`ovs-vswitchd` running)

### File Placement

```bash
cp host_discovery.py ~/pox/pox/host_discovery.py
```

***

## ▶️ Step 0 — Cleanup (Always Run First)

```bash
sudo mn -c
```

Clears old Mininet topology, stale OVS bridges, and leftover processes.

***

## ▶️ Step 1 — Start POX Controller (Terminal 1)

```bash
cd ~/pox
python3 pox.py log.level --DEBUG forwarding.l2_learning host_discovery
```

| Part | Meaning |
|------|---------|
| `log.level --DEBUG` | Show all events in real-time |
| `forwarding.l2_learning` | Built-in MAC learning switch module |
| `host_discovery` | Your custom module — prints NEW HOST DETECTED |

**Wait for:**
```
INFO:core:POX 0.7.0 (gar) is up.
```

> 🔴 Keep this terminal open — all `NEW HOST DETECTED` output appears here.

***

## ▶️ Step 2 — Start Mininet (Terminal 2)

```bash
sudo mn --controller=remote --topo=single,4 --mac
```

| Part | Meaning |
|------|---------|
| `--controller=remote` | Connect to external POX on 127.0.0.1:6633 |
| `--topo=single,4` | 1 switch + 4 hosts |
| `--mac` | Clean MACs: 00:00:00:00:00:01 etc. |

**Wait for:**
```
mininet>
```

***

## 🧪 Scenario 1 — Discover All Hosts (`pingall`)

```bash
mininet> pingall
```

Every host sends its first packet → triggers `packet_in` → controller detects each new host.

**Expected POX output (Terminal 1):**
```
==================================================
        NEW HOST DETECTED
==================================================
  MAC    : 00:00:00:00:00:01
  IP     : 10.0.0.1
  Switch : 1
  Port   : 1
==================================================

(repeats for h2, h3, h4)
```

**Expected Mininet output:**
```
*** Results: 0% dropped (12/12 received)
```

***

## 🧪 Scenario 2 — Ping a Specific Host

```bash
mininet> h1 ping -c 5 h4
```

**Other ping variants:**
```bash
mininet> h1 ping -c 1 h2        # ping once
mininet> h2 ping -c 10 h3       # ping 10 times
mininet> h1 ping -c 5 10.0.0.4  # ping by IP
mininet> h3 ping -c 3 h1        # h3 to h1
```

**Expected output:**
```
icmp_seq=1 time=15.3 ms   ← first ping (controller involved)
icmp_seq=2 time=0.18 ms   ← after flow rule installed
icmp_seq=3 time=0.11 ms
icmp_seq=4 time=0.10 ms
icmp_seq=5 time=0.09 ms
```

> First ping is slower (packet_in round trip). Later pings are sub-millisecond — proves reactive SDN flow installation works.

***

## 🧪 Scenario 3 — Verify Flow Table

```bash
mininet> sh ovs-ofctl dump-flows s1
```

**Expected output:**
```
cookie=0x0, duration=5.3s, table=0, n_packets=6,
  dl_dst=00:00:00:00:00:01 actions=output:1

cookie=0x0, duration=5.1s, table=0, n_packets=6,
  dl_dst=00:00:00:00:00:02 actions=output:2
```

> `n_packets` counter rising = switch forwarding directly using the flow rule.

***

## 🧪 Scenario 4 — Packet Capture

```bash
mininet> h1 tcpdump -i h1-eth0 -c 10 &
mininet> h2 ping -c 5 h1
```

**Expected tcpdump output:**
```
ICMP echo request from 10.0.0.2
ICMP echo reply  from 10.0.0.1
(5 request/reply pairs)
```

***

## 🧪 Scenario 5 — Detect Irregularity (Link Failure)

```bash
mininet> link s1 h2 down     # disconnect h2
mininet> pingall              # h2 shows as unreachable (X)
mininet> link s1 h2 up        # reconnect h2
mininet> pingall              # back to 0% drop
```

***

## 🧪 Scenario 6 — Port Statistics (Detect Abnormal Traffic)

```bash
mininet> sh ovs-ofctl dump-ports s1
```

Compare per-port counters. A port with abnormally high `rx pkts` signals a flooding host — detectable irregularity.

***

## 📊 Performance Metrics

| Metric | Command | Expected Result |
|--------|---------|----------------|
| Reachability | `pingall` | 0% dropped (12/12) |
| Latency | `h1 ping -c 5 h4` | First ~10ms, rest <1ms |
| Flow table | `ovs-ofctl dump-flows s1` | 1 rule per host |
| Packet capture | `tcpdump` | ICMP request/reply visible |

***

## 🗂️ Full Mininet CLI Reference

```bash
# Network Info
nodes                              # List all nodes
net                                # Show all links
dump                               # Node details (IP, PID, interface)
links                              # Show links with status

# Connectivity
pingall                            # Ping every host pair
pingpair                           # Ping between h1 and h2 only
h1 ping -c 5 h4                    # h1 pings h4 five times
h1 ping -c 1 10.0.0.4              # Ping by IP

# Flow Table
sh ovs-ofctl dump-flows s1         # Show all flow rules
sh ovs-ofctl dump-ports s1         # Per-port packet counters
sh ovs-ofctl del-flows s1          # Delete all flow rules
sh ovs-ofctl show s1               # Switch DPID and ports

# Packet Capture
h1 tcpdump -i h1-eth0 -c 10 &     # Capture 10 packets on h1

# Link Control
link s1 h2 down                    # Disconnect h2
link s1 h2 up                      # Reconnect h2

# Visual Terminals
xterm h1 h2 h3 h4                  # Open terminal per host

# Exit
exit                               # Quit Mininet
```

***

## 🔁 Reset Between Runs

```bash
mininet> exit
# Terminal 1: Ctrl+C
sudo mn -c
```

Restart from Step 1.

***

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| `Connection refused` on Mininet start | POX not running — start Terminal 1 first |
| `pingall` shows 100% drop | Controller not connected — check Terminal 1 |
| `No module named host_discovery` | Move file to `~/pox/pox/host_discovery.py` |
| `ovs-vswitchd not running` | `sudo systemctl start ovs-vswitchd ovsdb-server` |
| Old topology exists | Run `sudo mn -c` before starting |
| `iperf GLIBC error` | Use `iperf3`: `sudo pacman -S iperf3` |

***

## 🧠 Key SDN Concepts

| Term | Meaning |
|------|---------|
| **SDN** | Separates control plane (POX) from data plane (OVS) |
| **OpenFlow** | Protocol for controller-switch communication via TCP 6633 |
| **packet_in** | Event when switch has no matching flow rule |
| **TABLE MISS** | Condition triggering `packet_in` to controller |
| **Reactive Mode** | Flow rules installed on-demand after `packet_in` |
| **Flow Rule** | `<match, action, priority, timeout>` stored in switch |
| **DPID** | Unique 64-bit switch identifier |
| **TCAM** | Switch hardware for fast flow-rule lookup |
| **Northbound API** | Between controller and your app (host_discovery.py) |
| **Southbound API** | OpenFlow channel between POX and OVS on TCP 6633 |

***

## 📁 Project Structure

```
sdn-host-discovery/
├── README.md
├── host_discovery.py       ← POX module: packet_in + host_db
└── screenshots/
    ├── new_host_detected.png
    ├── pingall.png
    └── flow_table.png
```

***

## 📚 References

- [Mininet](http://mininet.org)
- [POX Controller](https://github.com/noxrepo/pox)
- [OpenFlow 1.0 Spec](https://opennetworking.org)
- [Open vSwitch](https://www.openvswitch.org)
