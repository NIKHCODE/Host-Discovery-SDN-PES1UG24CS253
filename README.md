# Host Discovery Service - SDN Project

## Problem Statement
Automatically detect and maintain a list of hosts in the SDN network.

## Objectives
- Detect host join events via PacketIn
- Maintain a dynamic host database (MAC, IP, Switch, Port)
- Display host details in real-time
- Update dynamically as hosts join/leave

## Network Topology
- 1 Switch (s1)
- 4 Hosts (h1, h2, h3, h4)
- Remote POX Controller (127.0.0.1:6633)

## Setup & Execution

### Prerequisites
- Arch Linux
- Mininet 2.3.1b4
- POX Controller (gar branch)
- Python 3.x
- Open vSwitch

### Installation
```bash
# Install Mininet
git clone https://github.com/mininet/mininet
cd mininet && sudo python3 setup.py install
sudo cp bin/mn /usr/local/bin/

# Clone POX
git clone https://github.com/noxrepo/pox ~/pox
```

### Running the Project

**Terminal 1 - Start POX Controller:**
```bash
cd ~/pox
python3 pox.py log.level --DEBUG forwarding.l2_learning host_discovery
```

**Terminal 2 - Start Mininet Topology:**
```bash
sudo mn --controller=remote --topo=single,4
```

**Inside Mininet CLI:**
pingall
h1 ping -c 5 h4
h1 tcpdump -i h1-eth0 -c 10 &
h2 ping -c 5 h1
sh ovs-ofctl dump-flows s1


## Expected Output
- POX terminal shows `NEW HOST DETECTED` for each host with MAC, IP, Switch, Port
- `pingall` shows 0% packet loss
- Flow table shows installed OpenFlow rules per host

## Test Scenarios
- **Scenario 1**: `pingall` - all 4 hosts communicate successfully
- **Scenario 2**: `h1 ping -c 5 h4` - direct host-to-host communication

## Performance Metrics
- Latency: measured via `ping` RTT
- Throughput: measured via `iperf`
- Flow table: verified via `ovs-ofctl dump-flows s1`

## References
- [Mininet](http://mininet.org)
- [POX Controller](https://github.com/noxrepo/pox)
- [OpenFlow Specification](https://opennetworking.org)
