import requests
import json
import time
from colorama import Fore, Style, init

init(autoreset=True)

def prompt_input(message, color=Fore.GREEN):
    print(f"{color}{message}{Style.RESET_ALL}")
    return input().strip()

def main():
    url = prompt_input("Please enter the URL:")
    apikey = prompt_input("Please enter the API key:")
    nodenum = prompt_input("Please enter the Node ID:")

    try:
        nodenum = int(nodenum)
    except ValueError:
        pass

    yes_or_no = prompt_input("Do you want to delete servers on this node? (y/n):", Fore.YELLOW)
    if yes_or_no.lower() != 'y':
        print(Fore.RED + "Operation cancelled.")
        return

    base_url = f'{url}/api/application/servers'
    headers = {
        "Authorization": f"Bearer {apikey}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    servers_on_node = []
    page = 1

    while True:
        params = {'page': page}
        response = requests.get(base_url, headers=headers, params=params)

        if response.status_code == 200 and 'application/json' in response.headers['Content-Type']:
            try:
                data = response.json()
                data_servers = data.get('data', [])
                if data_servers:
                    for server in data_servers:
                        if str(server['attributes']['node']) == str(nodenum):
                            servers_on_node.append(server)
                    page += 1
                else:
                    break
            except json.JSONDecodeError:
                print(Fore.RED + f"Response is not valid JSON: {response.text}")
                break
        else:
            print(Fore.RED + f"Invalid status code {response.status_code} or Content-Type: {response.headers['Content-Type']}")
            break

    server_count = len(servers_on_node)
    print(Fore.CYAN + "Number of servers on the node:", server_count)

    identifiers = [server['attributes']['id'] for server in servers_on_node]
    with open('server_identifiers.json', 'w') as file:
        json.dump(identifiers, file)

    time.sleep(1)

    confirm_delete = prompt_input("Are you sure you want to continue deleting? All servers on the node will be deleted. (y/n):", Fore.RED)
    if confirm_delete.lower() != 'y':
        print(Fore.RED + "Operation cancelled.")
        return

    print(Fore.YELLOW + "Deleting servers...")

    for identifier in identifiers:
        request_url = f'{base_url}/{identifier}/force'
        response = requests.delete(request_url, headers=headers)
        if response.status_code in [200, 204]:
            print(Fore.GREEN + f"Server with ID {identifier} deleted.")
        else:
            print(Fore.RED + f"Failed to delete server with ID {identifier}: {response.status_code} {response.text}")

    print(Fore.CYAN + "Deletion operation completed.")

if __name__ == "__main__":
    main()
