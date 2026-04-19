# Host Discovery Service — SDN Project

> Single-file README for an SDN Mininet + POX/OpenFlow project with setup, commands, diagrams, validation, and technical terms.

## Problem statement

This project implements an SDN-based host discovery service using Mininet and a POX/OpenFlow controller. The controller handles `packet_in` events, learns host details, installs explicit match-action flow rules, and demonstrates controller-switch interaction, flow-rule design, and observable network behavior.[file:2]

## What this shows

- SDN control plane and data plane separation using a software controller and Open vSwitch.[file:2]
- Explicit flow-rule installation with match/action behavior on traffic arrival.[file:2]
- Functional validation using `pingall`, direct `ping`, `iperf`, and flow-table inspection.[file:2][file:1]
- README-friendly proof of execution with expected outputs, logs, and screenshots.[file:2]

## Core terms

| Term | Meaning |
|---|---|
| **SDN** | Software-Defined Networking separates the control plane from the data plane so forwarding behavior is controlled in software.[file:2] |
| **POX** | A Python-based OpenFlow controller suitable for controller logic and `packet_in` handling in Mininet experiments.[file:2] |
| **OpenFlow** | A southbound protocol used for controller-switch interaction and explicit flow-rule installation.[file:2] |
| **Mininet** | A network emulator that creates realistic virtual hosts, switches, and links on a single Linux system.[file:1] |
| **Open vSwitch** | A software switch used by Mininet to forward packets and maintain flow tables.[file:1] |
| **packet_in** | A controller event generated when the switch needs the controller to decide how traffic should be handled.[file:2] |
| **Match-Action Rule** | A flow entry that matches packet fields and applies an action such as forwarding to a port.[file:2] |
| **DPID** | Datapath ID, the switch identifier seen by the controller in SDN applications.[file:2] |
| **Reactive forwarding** | Rules are installed after traffic appears, usually triggered by `packet_in`.[file:2] |
| **Flow table** | The switch data structure containing forwarding rules and counters.[file:2] |

## Architecture

```text
+---------------------------------------------------+
|                 Application Layer                 |
|              host_discovery.py module             |
+---------------------------------------------------+
|                  Control Layer                    |
|         POX Controller (OpenFlow control)         |
+---------------------------------------------------+
|                Infrastructure Layer               |
|       Open vSwitch in Mininet + virtual hosts     |
+---------------------------------------------------+
```

The assignment expects a Mininet topology with a POX or Ryu controller, explicit flow rules, and controller logic that handles `packet_in` with clear functional behavior.[file:2]

## Example topology

```text
                    POX Controller
                         |
                  OpenFlow channel
                         |
                        s1
                  /   /   |   \
                h1   h2   h3   h4
```

A single-switch topology is enough to demonstrate host learning, flow installation, and testing behavior clearly in Mininet.[file:1][file:2]

## Setup

These commands come from the Mininet installation guide and the SDN project requirements.

### Install Mininet

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install mininet -y
```

The Ubuntu installation guide recommends updating packages first and installing Mininet directly through the package manager for the simple setup path.[file:1]

### Alternative source install

```bash
sudo apt install git build-essential python3-pip -y
git clone https://github.com/mininet/mininet
cd mininet
sudo ./util/install.sh -a
```

The guide also provides an optional source-based installation path for advanced setups.[file:1]

### Verify Mininet

```bash
sudo mn
pingall
exit
```

A successful verification creates a default topology and `pingall` should report full connectivity with no packet loss.[file:1]

### Cleanup old state

```bash
sudo mn -c
```

The Mininet guide recommends cleaning previous configuration before retrying experiments.[file:1]

## Running the SDN demo

### Terminal 1 — start POX

```bash
cd ~/pox
python3 pox.py log.level --DEBUG forwarding.l2_learning host_discovery
```

The project brief requires a controller-driven Mininet demonstration with packet handling and explicit flow-rule logic, and this POX command is appropriate for a learning-switch-style host discovery demo.[file:2]

### Terminal 2 — start topology

```bash
sudo mn --controller=remote --topo=single,4
```

The Mininet guide documents `--topo single,3` as a valid single-switch pattern, so `single,4` is the same topology style with four hosts for richer testing.[file:1]

## Useful commands

```bash
# Inside Mininet CLI
nodes
net
dump
pingall
h1 ping -c 5 h4
sh ovs-ofctl dump-flows s1
h1 iperf -s &
h4 iperf -c 10.0.0.1 -t 5
exit
```

The Mininet manual explicitly lists `nodes`, `net`, `dump`, `pingall`, and `exit` as core commands, while the project brief expects validation using tools like `iperf` and flow tables in the README proof.[file:1][file:2]

## Controller logic

```text
Host sends packet
      |
      v
Switch checks flow table
      |
      +--> Match found --> forward using installed rule
      |
      +--> No match --> send packet_in to controller
                              |
                              v
                     Controller learns host details
                              |
                              v
                    Install match-action flow rule
                              |
                              v
                      Future packets switch locally
```

This behavior directly matches the assignment requirement to handle `packet_in`, implement match/action logic, and demonstrate flow-rule design and observed network behavior.[file:2]

## Accuracy and technical notes

- A first packet in reactive SDN is usually slower because the switch consults the controller before a rule exists; later packets are faster because forwarding happens via the installed flow entry.[file:2]
- `ping` is suitable for observing latency, `iperf` for throughput, and flow-table dumps for verifying rule installation and packet counters.[file:2]
- Mininet uses lightweight virtualization and network namespaces, which is why it can emulate realistic topologies efficiently on one machine.[file:1]
- Open vSwitch and virtual Ethernet links are the basis of host-switch connectivity in Mininet topologies.[file:1]

## Validation ideas

The project brief asks for at least two test scenarios and clear demonstration of behavior.[file:2]

- Scenario 1: Run `pingall` to verify end-to-end reachability across all hosts.[file:1][file:2]
- Scenario 2: Run `h1 ping -c 5 h4` and inspect logs plus `ovs-ofctl dump-flows s1` to correlate traffic with installed rules.[file:2]
- Scenario 3: Run `iperf` between two hosts to discuss throughput and forwarding behavior.[file:2]

## Expected observations

- The controller should show host-learning or packet-handling activity when new traffic arrives.[file:2]
- The switch flow table should gain entries representing the installed match-action behavior.[file:2]
- `pingall` should succeed when the topology and controller are correctly configured.[file:1]
- The README can include screenshots of logs, flow tables, Wireshark captures, and ping or iperf output as proof of execution.[file:2]

## What to include in GitHub

The final deliverable should contain the source code, public GitHub repository, complete README documentation, setup or execution steps, expected output, and proof of execution such as screenshots, logs, Wireshark output, and flow tables.[file:2]

## Suggested repo layout

```text
sdn-host-discovery/
├── README.md
├── host_discovery.py
├── topology.py
└── screenshots/
    ├── pingall.png
    ├── flow_table.png
    └── controller_logs.png
```

## Quick viva points

- Why SDN: centralized control and easier policy changes.[file:2]
- Why Mininet: rapid and realistic network emulation without physical hardware.[file:1]
- Why OpenFlow: clear controller-switch protocol for rule installation.[file:2]
- Why packet_in matters: it is the trigger for reactive decision-making and host discovery logic.[file:2]
