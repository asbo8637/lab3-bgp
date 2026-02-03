from sshinfo import load_json
from validateIPv4 import validate_ipv4_list
from connectivity import ping
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import time

import json
from netmiko import ConnectHandler

config = load_json()
value = validate_ipv4_list(config["IPS"])
print(f"Are IP's correct: {value}")
if not value:
    raise ValueError("Invalid IP list")

value = ping(config["IPS"])
print(f"Can I ping: {value}")
if not value:
    raise ValueError("Could not Ping")

with open("./bgp.conf", "r", encoding="utf-8") as f:
    data = json.load(f)

routers = data["Routers"]
file_lock = Lock()

def get_bgp_neighbor_state(conn, neighbor_ip: str) -> str:
    out = conn.send_command("show ip bgp summary")
    for line in out.splitlines():
        if line.strip().startswith(neighbor_ip):
            parts = line.split()
            state = parts[-1]
            print("BGP Neighbor IP \ BGP Neighbor AS \ BGP Neighbor State")
            print(f"{neighbor_ip}\ {parts[2]} \{state}")
            return state

    return "Unknown"



CONFIG_ERROR_PATTERN = r"%\s*(Invalid input|Incomplete command|Ambiguous command)"


def set_up_router(router, ssh_data, bgp_data, count, name):
    device = {
        "device_type": "cisco_ios",
        "host": ssh_data["IPS"][count],
        "username": ssh_data["user"],
        "password": ssh_data["pass"],
        "secret": ssh_data["pass"]
    }

    conn = ConnectHandler(**device)
    conn.enable()

    bgp_commands = [
        f"router bgp {router['local_asn']}",
        f"neighbor {router['neighbor_ip']} remote-as {router['neighbor_remote_as']}"
    ]

    for net in router["NetworkListToAdvertise"]:
        bgp_commands.append(f"network {net} mask 255.255.255.255")

    output = conn.send_config_set(bgp_commands, error_pattern=CONFIG_ERROR_PATTERN)

    print(f"BGP configured on {name}")

    time.sleep(2)
    neighbor_state = get_bgp_neighbor_state(conn, router["neighbor_ip"])
    with file_lock:
        bgp_data["Routers"][name]["neighbor_state"] = neighbor_state
        with open("./bgp.conf", "w", encoding="utf-8") as f:
            json.dump(bgp_data, f, indent=2)


    bgp_routes = conn.send_command("show ip route bgp")
    print(f"{name} BGP routes:")
    print(bgp_routes)

    running_config = conn.send_command("show running-config")
    running_config_file = f"./{name}-config.txt"
    with open(running_config_file, "w", encoding="utf-8") as f:
        f.write(running_config)
    print(f"Saved config to {running_config_file}")

    conn.disconnect()
    return neighbor_state



with ThreadPoolExecutor(max_workers=len(routers)) as executor:
    futures = []

    for count, (name, router) in enumerate(routers.items()):
        futures.append(executor.submit(set_up_router, router, config, data, count, name))

    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"Error during router setup: {e}")
