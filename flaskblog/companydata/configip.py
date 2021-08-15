import os

dhcpcd = ["interface eth0\n",
"static ip_address={ip}/24\n",
"static routers={ip_router}\n",
"static domain_name_servers={ip_router} 8.8.8.8\n"]


def create_ip_router(var_ip):

    new_ip = var_ip.split(".")
    return new_ip[0] + "." + new_ip[1] + "." + new_ip[2] + "." + "1"

def config_ip(var_ip):

    ip_router = create_ip_router(var_ip)

    a_file = open("/home/jorge/dhcpcd.conf", "r")
    list_of_lines = a_file.readlines()

    print(len(list_of_lines))

    if len(list_of_lines) > 60:

        list_of_lines[60] = dhcpcd[1].format( ip = var_ip )
        list_of_lines[61] = dhcpcd[2].format( ip_router = ip_router )
        list_of_lines[62] = dhcpcd[3].format( ip_router = ip_router )

    else:

        list_of_lines.append( dhcpcd[0] )
        list_of_lines.append( dhcpcd[1].format( ip = var_ip ) )
        list_of_lines.append( dhcpcd[2].format( ip_router = ip_router ) )
        list_of_lines.append( dhcpcd[3].format( ip_router = ip_router ) )

    a_file = open("/home/jorge/dhcpcd.conf", "w")
    a_file.writelines(list_of_lines)
    a_file.close()

    os.system('sudo reboot')
