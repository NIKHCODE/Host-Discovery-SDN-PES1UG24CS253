from pox.core import core
from pox.lib.packet.ethernet import ethernet
from pox.lib.packet.ipv4 import ipv4
from pox.lib.addresses import EthAddr, IPAddr
import pox.openflow.libopenflow_01 as of
from datetime import datetime

log = core.getLogger()

class HostDiscoveryService(object):

    def __init__(self):
        self.host_db = {}  # key: MAC address, value: host details
        core.openflow.addListeners(self)
        log.info("Host Discovery Service started...")
        log.info("-" * 55)

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            log.warning("Incomplete packet, ignoring.")
            return

        mac = str(packet.src)
        dpid = event.dpid        # switch ID
        port = event.port        # port host connected on

        # Extract IP if available
        ip = None
        ip_packet = packet.find('ipv4')
        if ip_packet:
            ip = str(ip_packet.srcip)

        # Check if host is new or updated
        if mac not in self.host_db:
            self.host_db[mac] = {
                'mac': mac,
                'ip': ip,
                'switch': dpid,
                'port': port,
                'first_seen': datetime.now().strftime("%H:%M:%S"),
                'last_seen': datetime.now().strftime("%H:%M:%S")
            }
            log.info("NEW HOST DETECTED")
            log.info("  MAC     : %s", mac)
            log.info("  IP      : %s", ip if ip else "Unknown")
            log.info("  Switch  : %s", dpid)
            log.info("  Port    : %s", port)
            log.info("  Time    : %s", self.host_db[mac]['first_seen'])
            log.info("-" * 55)
        else:
            # Update existing host entry
            old = self.host_db[mac]
            updated = False
            if ip and old['ip'] != ip:
                old['ip'] = ip
                updated = True
            if old['switch'] != dpid or old['port'] != port:
                old['switch'] = dpid
                old['port'] = port
                updated = True
            old['last_seen'] = datetime.now().strftime("%H:%M:%S")
            if updated:
                log.info("HOST UPDATED")
                log.info("  MAC     : %s", mac)
                log.info("  IP      : %s", old['ip'] if old['ip'] else "Unknown")
                log.info("  Switch  : %s", dpid)
                log.info("  Port    : %s", port)
                log.info("-" * 55)

        # Install a basic flow rule so traffic is forwarded
        msg = of.ofp_flow_mod()
        msg.match.dl_dst = EthAddr(mac)
        msg.actions.append(of.ofp_action_output(port=port))
        event.connection.send(msg)

    def display_hosts(self):
        log.info("=" * 55)
        log.info("CURRENT HOST DATABASE (%d hosts)", len(self.host_db))
        log.info("=" * 55)
        for mac, info in self.host_db.items():
            log.info("MAC: %s | IP: %s | SW: %s | Port: %s",
                     mac,
                     info['ip'] if info['ip'] else "Unknown",
                     info['switch'],
                     info['port'])
        log.info("=" * 55)


def launch():
    core.registerNew(HostDiscoveryService)
