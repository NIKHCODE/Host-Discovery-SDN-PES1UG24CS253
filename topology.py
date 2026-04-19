from mininet.net import Mininet
from mininet.node import RemoteController
from mininet.topo import SingleSwitchTopo
from mininet.log import setLogLevel
from mininet.cli import CLI

def run():
    setLogLevel('info')

    # Single switch topology with 4 hosts
    topo = SingleSwitchTopo(4)

    # Connect to remote POX controller
    net = Mininet(
        topo=topo,
        controller=RemoteController('c0', ip='127.0.0.1', port=6633)
    )

    net.start()
    print("\n*** Host Discovery Service Topology Started")
    print("*** Hosts:", [h.name for h in net.hosts])
    print("*** Switch:", [s.name for s in net.switches])
    print("*** Controller: POX running on 127.0.0.1:6633\n")

    CLI(net)
    net.stop()

if __name__ == '__main__':
    run()
