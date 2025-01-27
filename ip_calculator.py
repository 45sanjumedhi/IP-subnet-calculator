import ipaddress
import argparse
from os import system
from typing import Tuple


def classify_ip(address: str) -> str:
    first_octet = int(address.split('.')[0])
    if first_octet < 128:
        return "Class A"
    elif first_octet < 192:
        return "Class B"
    elif first_octet < 224:
        return "Class C"
    elif first_octet < 240:
        return "Class D"
    elif first_octet < 256:
        return "Class E"
    else:
        return "Out of range or invalid IP address"

# Create the parser
parser = argparse.ArgumentParser(description='SubnetWizard')

# Add the arguments
ip_help = "The IPv4 address to calculate\nExample: 192.168.0.100/24 or 10.0.0.1/255.255.255.0\nSupports both CIDR and Subnet Mask after the slash"
parser.add_argument('-i', dest='ip', type=str, help=ip_help)
subnet_help = "The netmask to subnet (optional)"
parser.add_argument('-s', dest='subnet', type=str, help=subnet_help)

def display_logo() -> None:
    print("MADE BY SANJU MEDHI")

def get_network(ip: str = None) -> Tuple[ipaddress.IPv4Network, str]:
    if ip:
        try:
            if "/" not in ip: ip += "/24"
            net = ipaddress.IPv4Network(ip, strict=False)
            ip = ip.split("/")[0]
            return (net, ip)
        except ValueError:
            print("Invalid IP Address!")
            exit(1)
    while True:
        try:
            print("Enter an IP Address: ", end="")
            in_ = input()
            if in_ == "": in_ = "192.168.0.100/24"
            if "/" not in in_: in_ += "/24"
            net = ipaddress.IPv4Network(in_, strict=False)
            ip = in_.split("/")[0]
            return (net, ip)
        except ValueError:
            print("Invalid IP Address!")
            continue

def get_subnet(subnet: str = None) -> str:
    if subnet:
        if subnet == "0": 
            print("Invalid Netmask!")
            exit(1)
        try:
            net = ipaddress.IPv4Network(f"10.0.0.0/{subnet}", strict=False)
            return str(net.prefixlen)
        except ValueError:
            print("Invalid Netmask!")
            exit(1)
    while True:
        try:
            print("Enter a Netmask to subnet (optional): ", end="")
            in_ = input()
            if in_ == "0": 
                print("Invalid Netmask!")
                continue
            if in_ == "": return None
            net = ipaddress.IPv4Network(f"10.0.0.0/{in_.strip('/')}", strict=False)
            return str(net.prefixlen)
        except ValueError:
            print("Invalid Netmask!")
            continue

def calculate(network: Tuple[ipaddress.IPv4Network, str], subnet: str) -> None:
    ip = network[1]
    network = network[0]

    # Classify IP
    ip_class = classify_ip(ip)

    # Get the network and broadcast addresses
    network_address = network.network_address
    broadcast_address = network.broadcast_address
    usable_hosts = list(network.hosts())

    # Calculate the number of usable hosts
    num_usable_hosts = len(usable_hosts)

    # Format the usable hosts
    usable_hosts = f"{usable_hosts[0]} - {usable_hosts[-1]}" if usable_hosts else "NA"

    # Convert the IP address to binary
    octets = str(ip).split('.')
    binary_octets = [bin(int(octet))[2:].zfill(8) for octet in octets]
    bin_ip = '.'.join(binary_octets)

    bin_addr = str(bin(int(network_address))[2:].zfill(32))
    bin_addr = '.'.join([bin_addr[i:i+8] for i in range(0, len(bin_addr), 8)])

    bin_mask = str(bin(int(network.netmask))[2:].zfill(32))
    bin_mask = '.'.join([bin_mask[i:i+8] for i in range(0, len(bin_mask), 8)])

    # Print the results
    print(f"IP Address:             {ip}")
    print(f"IP Address (bin):       {bin_ip}")
    print(f"IP Class:               {ip_class}")
    print(f"Network Address:        {network_address}")
    print(f"Network Address (bin):  {bin_addr}")
    print(f"CIDR Notation:          /{network.prefixlen}")
    print(f"Broadcast Address:      {broadcast_address}")
    print(f"Usable IP Range:        {usable_hosts}")
    print(f"Number of Hosts:        {network.num_addresses:,d}")
    print(f"Number of Usable Hosts: {num_usable_hosts:,d}") 
    print(f"Wildcard Mask:          {network.hostmask}")
    print(f"Private IP:             {network.is_private}")
    print()

    if subnet is None or int(subnet) == int(network.prefixlen):
        return
    
    if int(subnet) > int(network.prefixlen): 
        print("Subnetted Network Details:\n")
        subnets = list(network.subnets(new_prefix=int(subnet)))
        print(f"Netmask:                {subnets[0].netmask}")
        print(f"Wildcard Mask:          {subnets[0].hostmask}")
        print(f"CIDR Notation:          /{int(subnet)}")
        print(f"Hosts per network:      {2 ** (32 - int(subnet)) - 2:,d}")

        if int(subnet) == 32: 
            return

        print("\n{:<15} | {:^31} | {:<15}".format(
            "Network Address", "Host Range", "Broadcast Address"))
        print("-" * 72)
        for subnet in subnets:
            host_range = list(subnet.hosts())
            host_range = host_range if len(host_range) > 1 else [host_range[0], host_range[0]]
            print("{:<24} | {:<22} - {:>24} | {:<24}".format(
                f"{subnet.network_address}", f"{host_range[0]}", 
                f"{host_range[-1]}", f"{subnet.broadcast_address}"
                ))
    else: 
        print("Supernetted Network Details:\n")
        subnets = network.supernet(new_prefix=int(subnet))
        print(f"Netmask:                {subnets.netmask}")
        print(f"Wildcard Mask:          {subnets.hostmask}")
        print(f"CIDR Notation:          /{int(subnet)}")
        print(f"Hosts/Network:          {2 ** (32 - int(subnet)) - 2:,d}")
        
        print("\n{:<15} | {:^31} | {:<15}".format(
            "Network Address", "Host Range", "Broadcast Address"))
        print("-" * 72)
        print("{:<24} | {:<22} - {:>24} | {:<24}".format(
            f"{subnets.network_address}", f"{subnets[0]}", 
            f"{subnets[-2]}", f"{subnets.broadcast_address}"
            ))
    print()

def main():
    display_logo()
    

    args = parser.parse_args()
    
    ip = args.ip if args.ip else None
    subnet = args.subnet if args.subnet else None

    network = get_network(ip)
    subnet = get_subnet(subnet)

    print()
    calculate(network, subnet)

if __name__ == "__main__":
    main()
