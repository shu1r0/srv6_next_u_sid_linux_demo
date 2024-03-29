from mininet.log import setLogLevel
from ipnet import IPNetwork, IPNode, CLIX

"""
ルーティングテーブルの設定どうするか問題
fdbb:bbbb::になったらどうなるの問題
encap.red???
"""


n1_conf = """\
configure terminal
interface n1_h1
  ipv6 address fd00:a::1/64
  ipv6 router isis 1
interface n1_n2
  ipv6 address fd00:12::1/64
  ipv6 router isis 1
interface n1_n3
  ipv6 address fd00:13::1/64
  ipv6 router isis 1
interface lo
  ipv6 address fdbb:bbbb:0100::/40
  ipv6 router isis 1

router isis 1
  net 49.0000.0000.0000.0001.00
  is-type level-1
exit

"""

n2_conf = """\
configure terminal
interface n2_h2
  ipv6 address fd00:b::1/64
  ipv6 router isis 1
interface n2_n1
  ipv6 address fd00:12::2/64
  ipv6 router isis 1
interface n2_n4
  ipv6 address fd00:24::1/64
  ipv6 router isis 1
interface lo
  ipv6 address fdbb:bbbb:0200::/40
  ipv6 router isis 1

router isis 1
  net 49.0000.0000.0000.0002.00
  is-type level-1
exit

"""

n3_conf = """\
configure terminal
interface n3_n1
  ipv6 address fd00:13::2/64
  ipv6 router isis 1
interface n3_n4
  ipv6 address fd00:34::1/64
  ipv6 router isis 1
interface n3_n5
  ipv6 address fd00:35::1/64
  ipv6 router isis 1
interface lo
  ipv6 address fdbb:bbbb:0300::/40
  ipv6 router isis 1

router isis 1
  net 49.0000.0000.0000.0003.00
  is-type level-1
exit

"""

n4_conf = """\
configure terminal
interface n4_n2
  ipv6 address fd00:24::2/64
  ipv6 router isis 1
interface n4_n3
  ipv6 address fd00:34::2/64
  ipv6 router isis 1
interface n4_n6
  ipv6 address fd00:46::1/64
  ipv6 router isis 1
interface lo
  ipv6 address fdbb:bbbb:0400::/40
  ipv6 router isis 1

router isis 1
  net 49.0000.0000.0000.0004.00
  is-type level-1
exit

"""

n5_conf = """\
configure terminal
interface n5_n3
  ipv6 address fd00:35::1/64
  ipv6 router isis 1
interface n5_n6
  ipv6 address fd00:56::1/64
  ipv6 router isis 1
interface lo
  ipv6 address fdbb:bbbb:0500::/40
  ipv6 router isis 1

router isis 1
  net 49.0000.0000.0000.0005.00
  is-type level-1
exit

"""

n6_conf = """\
configure terminal
interface n6_n4
  ipv6 address fd00:46::2/64
  ipv6 router isis 1
interface n6_n5
  ipv6 address fd00:56::2/64
  ipv6 router isis 1
interface lo
  ipv6 address fdbb:bbbb:0600::/40
  ipv6 router isis 1

router isis 1
  net 49.0000.0000.0000.0006.00
  is-type level-1
exit

"""


def main():
    setLogLevel("info")
    net = IPNetwork()

    h1 = net.addHost("h1", cls=IPNode)
    h2 = net.addHost("h2", cls=IPNode)
    n1 = net.addFRR("n1", enable_daemons=["isisd", "staticd"])
    n2 = net.addFRR("n2", enable_daemons=["isisd", "staticd"])
    n3 = net.addFRR("n3", enable_daemons=["isisd", "staticd"])
    n4 = net.addFRR("n4", enable_daemons=["isisd", "staticd"])
    n5 = net.addFRR("n5", enable_daemons=["isisd", "staticd"])
    n6 = net.addFRR("n6", enable_daemons=["isisd", "staticd"])

    net.addLink(h1, n1, intfName1="h1_n1", intfName2="n1_h1")
    net.addLink(h2, n2, intfName1="h2_n2", intfName2="n2_h2")
    net.addLink(n1, n2, intfName1="n1_n2", intfName2="n2_n1")
    net.addLink(n1, n3, intfName1="n1_n3", intfName2="n3_n1")
    net.addLink(n2, n4, intfName1="n2_n4", intfName2="n4_n2")
    net.addLink(n3, n4, intfName1="n3_n4", intfName2="n4_n3")
    net.addLink(n3, n5, intfName1="n3_n5", intfName2="n5_n3")
    net.addLink(n4, n6, intfName1="n4_n6", intfName2="n6_n4")
    net.addLink(n5, n6, intfName1="n5_n6", intfName2="n6_n5")

    h1.set_ipv6_cmd("fd00:a::2/64", "h1_n1")
    h1.cmd("ip -6 route add default dev h1_n1 via fd00:a::1")
    h2.set_ipv6_cmd("fd00:b::2/64", "h2_n2")
    h2.cmd("ip -6 route add default dev h2_n2 via fd00:b::1")

    net.start()

    n1.vtysh_cmd(n1_conf)
    n2.vtysh_cmd(n2_conf)
    n3.vtysh_cmd(n3_conf)
    n4.vtysh_cmd(n4_conf)
    n5.vtysh_cmd(n5_conf)
    n6.vtysh_cmd(n6_conf)

    n1.cmd("ip -6 route replace fdbb:bbbb:0100::/48 encap seg6local action End flavors next-csid dev n1_n2", verbose=True)
    n1.cmd("ip -6 route add fdbb:bbbb:f00d::/48 encap seg6local action End.DT6 table 0 dev n1_n2", verbose=True)
    n1.cmd("ip -6 route add fdbb:bbbb:0100::/64 encap seg6local action End flavors psp dev n1_n2", verbose=True)
    n2.cmd("ip -6 route replace fdbb:bbbb:0200::/48 encap seg6local action End flavors next-csid dev n2_n1", verbose=True)
    n2.cmd("ip -6 route add fdbb:bbbb:f00d::/48 encap seg6local action End.DT6 table 0 dev n2_n1", verbose=True)
    n2.cmd("ip -6 route add fdbb:bbbb:0200::/64 encap seg6local action End flavors psp dev n2_n1", verbose=True)
    n3.cmd("ip -6 route replace fdbb:bbbb:0300::/48 encap seg6local action End flavors next-csid dev n3_n4", verbose=True)
    n3.cmd("ip -6 route add fdbb:bbbb:0300::/64 encap seg6local action End flavors psp dev n3_n4", verbose=True)
    n4.cmd("ip -6 route replace fdbb:bbbb:0400::/48 encap seg6local action End flavors next-csid dev n4_n3", verbose=True)
    n4.cmd("ip -6 route add fdbb:bbbb:0400::/64 encap seg6local action End flavors psp dev n4_n3", verbose=True)
    n5.cmd("ip -6 route replace fdbb:bbbb:0500::/48 encap seg6local action End flavors next-csid dev n5_n6", verbose=True)
    n5.cmd("ip -6 route add fdbb:bbbb:0500::/64 encap seg6local action End flavors psp dev n5_n6", verbose=True)
    n6.cmd("ip -6 route replace fdbb:bbbb:0600::/48 encap seg6local action End flavors next-csid dev n6_n5", verbose=True)
    n6.cmd("ip -6 route add fdbb:bbbb:0600::/64 encap seg6local action End flavors psp dev n6_n5", verbose=True)
    
    # n1.cmd("ip -6 route add fd00:b::2/128 encap seg6 mode encap.red segs fdbb:bbbb:0500:0200:f00d:: dev n1_h1", verbose=True)
    n1.cmd("ip -6 route add fd00:b::2/128 encap seg6 mode encap segs fdbb:bbbb:0600::,fdbb:bbbb:0500:0200:f00d:: dev n1_h1", verbose=True)
    n2.cmd("ip -6 route add fd00:a::2/128 encap seg6 mode encap.red segs fdbb:bbbb:0600:0100:f00d:: dev n2_h2", verbose=True)
    
    h1.cmd("tcpdump -i h1_n1 -w captures/h1_n1.pcap &")
    h2.cmd("tcpdump -i h2_n2 -w captures/h2_n2.pcap &")
    n1.cmd("tcpdump -i n1_n2 -w captures/n1_n2.pcap &")
    n1.cmd("tcpdump -i n1_n3 -w captures/n1_n3.pcap &")
    n2.cmd("tcpdump -i n2_n4 -w captures/n2_n4.pcap &")
    n3.cmd("tcpdump -i n3_n4 -w captures/n3_n4.pcap &")
    n3.cmd("tcpdump -i n3_n5 -w captures/n3_n5.pcap &")
    n4.cmd("tcpdump -i n4_n6 -w captures/n4_n6.pcap &")
    n5.cmd("tcpdump -i n5_n6 -w captures/n5_n6.pcap &")
    n1.cmd("tcpdump -i n1_h1 -w captures/n1_h1.pcap &")
    n2.cmd("tcpdump -i n2_h2 -w captures/n2_h2.pcap &")
    n2.cmd("tcpdump -i n2_n1 -w captures/n2_n1.pcap &")
    n3.cmd("tcpdump -i n3_n1 -w captures/n3_n1.pcap &")
    n4.cmd("tcpdump -i n4_n2 -w captures/n4_n2.pcap &")
    n4.cmd("tcpdump -i n4_n3 -w captures/n4_n3.pcap &")
    n5.cmd("tcpdump -i n5_n3 -w captures/n5_n3.pcap &")
    n6.cmd("tcpdump -i n6_n4 -w captures/n6_n4.pcap &")
    n6.cmd("tcpdump -i n6_n5 -w captures/n6_n5.pcap &")

    CLIX(net)

    net.stop()


if __name__ == '__main__':
    main()