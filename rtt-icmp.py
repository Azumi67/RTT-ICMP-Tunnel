#
# ICMP + RTT tunnel Configuration Script
# Author: github.com/Azumi67
# Tunnel Author : github.com/radkesvat
# This is for educational use and my own learning, please provide me with feedback if possible
# There maybe some erros , please forgive me as i have worked on it while i was studying.
# This script is designed to simplify the configuration of ICMP combined with RTT Tunnel.
#
# Supported operating systems: Ubuntu 20, Debian 12
#
# Usage:
#   - Run the script with root privileges.
#   - Follow the on-screen prompts to install, configure, or uninstall the tunnel.
# I use the same imports and other stuff to speed up in creating the script
# you should only install colorama & netifaces
# Disclaimer:
# This script comes with no warranties or guarantees. Use it at your own risk.
import sys
import os
import time
import colorama
from colorama import Fore, Style
import subprocess
from time import sleep
import readline
import random
import string
import shutil
import netifaces as ni
import urllib.request
import zipfile

if os.geteuid() != 0:
    print("\033[91mThis script must be run as root. Please use sudo -i.\033[0m")
    sys.exit(1)


def display_progress(total, current):
    width = 40
    percentage = current * 100 // total
    completed = width * current // total
    remaining = width - completed

    print('\r[' + '=' * completed + '>' + ' ' * remaining + '] %d%%' % percentage, end='')


def display_checkmark(message):
    print('\u2714 ' + message)


def display_error(message):
    print('\u2718 Error: ' + message)


def display_notification(message):
    print('\u2728 ' + message)


def display_loading():
    duration = 3
    end_time = time.time() + duration
    ball_width = 10
    ball_position = 0
    ball_direction = 1

    while time.time() < end_time:
        sys.stdout.write('\r\033[93mLoading, Please wait... [' + ' ' * ball_position + 'o' + ' ' * (ball_width - ball_position - 1) + ']')
        sys.stdout.flush()

        if ball_position == 0:
            ball_direction = 1
        elif ball_position == ball_width - 1:
            ball_direction = -1

        ball_position += ball_direction
        time.sleep(0.1)
    
    sys.stdout.write('\r' + ' ' * (len('Loading, Please wait...') + ball_width + 4) + '\r')
    sys.stdout.flush()
    display_notification("\033[96mIt might take a while...\033[0m")
    
def display_logo2():
    colorama.init()
    logo2 = colorama.Style.BRIGHT + colorama.Fore.GREEN + """
     _____       _     _      
    / ____|     (_)   | |     
   | |  __ _   _ _  __| | ___ 
   | | |_ | | | | |/ _` |/ _ \\
   | |__| | |_| | | (_| |  __/
    \_____|\__,_|_|\__,_|\___|
""" + colorama.Style.RESET_ALL
    print(logo2)
    
def display_logo():
    colorama.init()
    logo = """
    ⠀⠀    \033[1;96m       ⠄⠠⠤⠤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀   ⠀⠀⢀⠠⢀⣢⣈⣉⠁⡆⠀⠀⠀⠀⠀⠀
⠀⠀             ⠀⡏⢠⣾⢷⢶⣄⣕⠢⢄⠀⠀⣀⣠⠤⠔⠒⠒⠒⠒⠒⠒⠢⠤⠄⣀⠤⢊⣤⣶⣿⡿⣿⢹⢀⡇⠀⠀⠀⠀⠀⠀
⠀⠀             ⠀⢻⠈⣿⢫⡞⠛⡟⣷⣦⡝⠋⠉⣤⣤⣶⣶⣶⣿⣿⣿⡗⢲⣴⠀⠈⠑⣿⡟⡏⠀⢱⣮⡏⢨⠃⠀⠀⠀⠀⠀⠀
⠀⠀             ⠀⠸⡅⣹⣿⠀⠀⢩⡽⠋⣠⣤⣿⣿⣏⣛⡻⠿⣿⢟⣹⣴⢿⣹⣿⡟⢦⣀⠙⢷⣤⣼⣾⢁⡾⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀             ⠀⢻⡀⢳⣟⣶⠯⢀⡾⢍⠻⣿⣿⣽⣿⣽⡻⣧⣟⢾⣹⡯⢷⡿⠁⠀⢻⣦⡈⢿⡟⠁⡼⠁⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀             ⠀⢷⠠⢻⠏⢰⣯⡞⡌⣵⠣⠘⡉⢈⠓⡿⠳⣯⠋⠁⠀⠀⢳⡀⣰⣿⣿⣷⡈⢣⡾⠁⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀             ⠀⠀⠙⣎⠀⣿⣿⣷⣾⣷⣼⣵⣆⠂⡐⢀⣴⣌⠀⣀⣤⣾⣿⣿⣿⣿⣿⣿⣷⣀⠣⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀            ⠀⠀  ⠄⠑⢺⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣳⣿⢽⣧⡤⢤⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀            ⠀⠀  ⢸⣈⢹⣟⣿⣿⣿⣿⣿⣻⢹⣿⣻⢿⣿⢿⣽⣳⣯⣿⢷⣿⡷⣟⣯⣻⣽⠧⠾⢤⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀             ⠀ ⢇⠤⢾⣟⡾⣽⣿⣽⣻⡗⢹⡿⢿⣻⠸⢿⢯⡟⡿⡽⣻⣯⣿⣎⢷⣣⡿⢾⢕⣎⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀             ⠀⡠⡞⡟⣻⣮⣍⡛⢿⣽⣻⡀⠁⣟⣣⠿⡠⣿⢏⡞⠧⠽⢵⣳⣿⣺⣿⢿⡋⠙⡀⠇⠱⠀⠀⠀
⠀⠀⠀             ⠀⢰⠠⠁⠀⢻⡿⣛⣽⣿⢟⡁\033[1;91m⣭⣥⣅⠀⠀⠀⠀⠀⠀⣶⣟⣧\033[1;96m⠿⢿⣿⣯⣿⡇⠀⡇⠀⢀⡇⠀⠀⠀⠀⠀⠀
⠀⠀             ⠀⠀⢸⠀⠀⡇⢹⣾⣿⣿⣷⡿⢿\033[1;91m⢷⡏⡈⠀⠀⠀⠀⠀⠀⠈⡹⡷⡎\033[1;96m⢸⣿⣿⣿⡇⠀⡇⠀⠸⡇⠀⠀⠀⠀⠀⠀
⠀             ⠀⠀⠀⢸⡄⠂⠖⢸⣿⣿⣿⡏⢃⠘\033[1;91m⡊⠩⠁⠀⠀⠀⠀⠀⠀⠀⠁⠀⠁\033[1;96m⢹⣿⣿⣿⡇⢰⢁⡌⢀⠇⠀⠀⠀⠀⠀⠀
⠀⠀             ⠀⠀⠀⢷⡘⠜⣤⣿⣿⣿⣷⡅⠐⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣧⣕⣼⣠⡵⠋⠀⠀⠀⠀⠀⠀⠀
⠀⠀              ⠀⠀⠀⣸⣻⣿⣾⣿⣿⣿⣿⣾⡄⠀⠀⠀⠀⠀⢀⣀⠀⠀⠀⠀⠀⣠⣿⣿⣿⣿⣿⣿⣿⢀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀             ⠀⠀⡇⣿⣻⣿⣿⣿⣿⣿⣿⣿⣦⣤⣀⠀⠀⠀⠀⠀⠀⣠⣴⣾⣿⣿⣿⣿⣿⣿⣳⣿⡸⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀             ⠀⠀\033[1;96m⣸⢡⣿⢿⣿⣿⣿⣿⣿⣿⣿⢿⣿⡟⣽⠉⠀⠒⠂⠉⣯⢹⣿⡿⣿⣿⣿⣿⣿⣯⣿⡇⠇ ⡇ \033[1;92mAuthor: github.com/Azumi67  \033[1;96m⡇⠀⠀⠀⠀⠀⠀⠀
⠀⠀             ⠀\033[1;96m⢰⡏⣼⡿⣿⣻⣿⣿⣿⣿⣿⢿⣻⡿⠁⠘⡆⠀⠀⠀⢠⠇⠘⣿⣿⣽⣿⣿⣿⣿⣯⣿⣷⣸⠀⡇ \033[1;96mTunnel Author: github.com/radkesvat\033[1;96m⡇⠀⠀
  \033[1;96m  ______   \033[1;94m _______  \033[1;92m __    \033[1;93m  _______     \033[1;91m    __      \033[1;96m  _____  ___  
 \033[1;96m  /    " \  \033[1;94m|   __ "\ \033[1;92m|" \  \033[1;93m  /"      \    \033[1;91m   /""\     \033[1;96m (\"   \|"  \ 
 \033[1;96m // ____  \ \033[1;94m(. |__) :)\033[1;92m||  |  \033[1;93m|:        |   \033[1;91m  /    \   \033[1;96m  |.\\   \    |
 \033[1;96m/  /    ) :)\033[1;94m|:  ____/ \033[1;92m|:  |  \033[1;93m|_____/   )   \033[1;91m /' /\  \   \033[1;96m |: \.   \\  |
\033[1;96m(: (____/ // \033[1;94m(|  /     \033[1;92m|.  | \033[1;93m //       /   \033[1;91m //  __'  \  \033[1;96m |.  \    \ |
 \033[1;96m\        / \033[1;94m/|__/ \   \033[1;92m/\  |\ \033[1;93m |:  __   \  \033[1;91m /   /  \\   \ \033[1;96m |    \    \|
 \033[1;96m \"_____ / \033[1;94m(_______) \033[1;92m(__\_|_)\033[1;93m |__|  \___) \033[1;91m(___/    \___) \033[1;96m\___|\____\)
"""
    print(logo)
def main_menu():
    try:
        while True:
            display_logo()
            border = "\033[93m+" + "="*70 + "+\033[0m"
            content = "\033[93m║            ▌║█║▌│║▌│║▌║▌█║ \033[92mMain Menu\033[93m  ▌│║▌║▌│║║▌█║▌                  ║"
            footer = " \033[92m            Join Opiran Telegram \033[34m@https://t.me/OPIranClub\033[0m "

            border_length = len(border) - 2
            centered_content = content.center(border_length)

            print(border)
            print(centered_content)
            print(border)
            display_status()

            print(border)
            print(footer)
            print(border)
            print("1. \033[96mRTT [TCP] + Hans icmp \033[0m")
            print("2. \033[93mRTT [TCP] + Icmptunnel \033[0m")
            print("3. \033[96mRTT \033[92m[UDP]\033[96m + Hans icmp \033[0m")
            print("4. \033[93mRTT \033[92m[UDP]\033[93m + Icmptunnel \033[0m")
            print("5. \033[92mStop | Restart Service \033[0m")
            print("6. \033[91mUninstall\033[0m")
            print("0. Exit")
            print("\033[93m╰─────────────────────────────────────────────────────────────────────╯\033[0m")

            choice = input("\033[5mEnter your choice Please: \033[0m")
            print("choice:", choice)
            if choice == '1':
                hans_rtt_menu()
            elif choice == '2':
                ic_rtt_menu()
            elif choice == '3':
                hans_rtt_udp()
            elif choice == '4':
                ic_rtt_udp()
            elif choice == '5':
                start_serv()
            elif choice == '6':
                uni_menu()
            elif choice == '0':
                print("Exiting...")
                break
            else:
                print("Invalid choice.")

            input("Press Enter to continue...")

    except KeyboardInterrupt:
        display_error("\033[91m\nProgram interrupted. Exiting...\033[0m")
        sys.exit()
def reset_icmp():
    try:
        reset_ipv4 = False
        reset_ipv6 = False

        os.system("sysctl -w net.ipv4.icmp_echo_ignore_all=0")
        reset_ipv4 = True

        os.system("sudo sysctl -w net.ipv6.icmp.echo_ignore_all=0")
        reset_ipv6 = True

        if reset_ipv4 or reset_ipv6:
            display_checkmark("\033[92mICMP has been reset to default!\033[0m")
        else:
            display_notification("\033[93mICMP settings has been reset.\033[0m")
    except Exception as e:
        display_error("\033[91mAn error occurred: {}\033[0m".format(str(e)))
	    
def uni_menu():
    os.system("clear")
    print('\033[92m ^ ^\033[0m')
    print('\033[92m(\033[91mO,O\033[92m)\033[0m')
    print('\033[92m(   ) \033[93mUninstall Menu\033[0m')
    print('\033[92m "-"\033[93m══════════════════════════\033[0m')
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print('\033[93mChoose what to do:\033[0m')
    print('1. \033[92mRTT + Hans \033[0m')
    print('2. \033[93mRTT + Icmptunnel \033[0m')
    print('3. \033[94mBack to the main menu\033[0m')
    print("\033[93m╰───────────────────────────────────────╯\033[0m")

    while True:
        server_type = input('\033[38;5;205mEnter your choice Please: \033[0m')
        if server_type == '1':
            remove_hans_tcp()
            break
        elif server_type == '2':
            remove_icmp_tcp()
            break
        elif server_type == '3':
            os.system("clear")
            main_menu()
            break
        else:
            print('Invalid choice.')
            
def remove_hans_tcp():
    os.system("clear")
    display_notification("\033[93mRemoving Hans + RTT ...\033[0m")
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    reset_icmp()
    try:
        if subprocess.call("test -f /etc/hans.sh", shell=True) == 0:
            subprocess.run("rm /etc/hans.sh", shell=True)

        display_notification("\033[93mRemoving cronjob...\033[0m")
        subprocess.run("crontab -l | grep -v \"@reboot /bin/bash /etc/hans.sh\" | crontab -", shell=True)
        time.sleep(1)
        subprocess.run("systemctl disable radkesvattunnel-kharej.service > /dev/null 2>&1", shell=True)
        subprocess.run("systemctl stop radkesvattunnel-kharej.service > /dev/null 2>&1", shell=True)
        subprocess.run("rm /etc/systemd/system/radkesvattunnel-kharej.service > /dev/null 2>&1", shell=True)
        time.sleep(1)
        subprocess.run("systemctl disable radkesvattunnel-iran.service > /dev/null 2>&1", shell=True)
        subprocess.run("systemctl stop radkesvattunnel-iran.service > /dev/null 2>&1", shell=True)
        subprocess.run("rm /etc/systemd/system/radkesvattunnel-iran.service > /dev/null 2>&1", shell=True)

        subprocess.run("systemctl daemon-reload", shell=True)
        subprocess.run("ip link set dev icmp down > /dev/null", shell=True)

        print("Progress: ", end="")

        try:

            lsof_process = subprocess.Popen(["lsof", "/root/hans-1.1/hans"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lsof_output, lsof_error = lsof_process.communicate()

            if lsof_output:
                pid = lsof_output.decode().split('\n')[1].split()[1]
                subprocess.run(["kill", pid])

            subprocess.run(["rm", "-rf", "/root/hans-1.1"])
        except FileNotFoundError:
            print("Error: Directory '/root/hans-1.1' does not exist.")

        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        delay = 0.1
        duration = 3
        end_time = time.time() + duration

        while time.time() < end_time:
            for frame in frames:
                print("\r[%s] Loading...  " % frame, end="")
                time.sleep(delay)
                print("\r[%s]             " % frame, end="")
                time.sleep(delay)

        display_checkmark("\033[92mUninstall completed!\033[0m")
    except Exception as e:
        print("An error occurred during uninstallation:", str(e))
    except subprocess.CalledProcessError as e:
        print("Error:", e.output.decode().strip())
            
def remove_icmp_tcp():
    os.system("clear")
    display_notification("\033[93mRemoving icmptunnel...\033[0m")
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    reset_icmp()
    try:
        if os.path.isfile("/etc/icmp.sh"):
            os.remove("/etc/icmp.sh")

        display_notification("\033[93mRemoving cronjob...\033[0m")
        subprocess.run("crontab -l | grep -v \"@reboot /bin/bash /etc/icmp.sh\" | crontab -", shell=True)

        time.sleep(1)
        subprocess.run("systemctl disable radkesvattunnel-kharej.service > /dev/null 2>&1", shell=True)
        subprocess.run("systemctl stop radkesvattunnel-kharej.service > /dev/null 2>&1", shell=True)
        subprocess.run("rm /etc/systemd/system/radkesvattunnel-kharej.service > /dev/null 2>&1", shell=True)
        time.sleep(1)
        subprocess.run("systemctl disable radkesvattunnel-iran.service > /dev/null 2>&1", shell=True)
        subprocess.run("systemctl stop radkesvattunnel-iran.service > /dev/null 2>&1", shell=True)
        subprocess.run("rm /etc/systemd/system/radkesvattunnel-iran.service > /dev/null 2>&1", shell=True)
        subprocess.run("ip link set dev tun0 down > /dev/null", shell=True)

        subprocess.run("systemctl daemon-reload", shell=True)

        print("Progress: ", end="")

        try:
            lsof_process = subprocess.Popen(["lsof", "-t", "/root/icmptunnel/icmptunnel"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            lsof_output, lsof_error = lsof_process.communicate()

            if lsof_output:
                pids = lsof_output.decode().split('\n')[:-1]
                for pid in pids:
                    subprocess.run(["kill", pid])

            subprocess.run(["rm", "-rf", "/root/icmptunnel"])
        except FileNotFoundError:
            print("Error: Directory '/root/icmptunnel' does not exist.")

        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        delay = 0.1
        duration = 3
        end_time = time.time() + duration

        while time.time() < end_time:
            for frame in frames:
                print("\r[%s] Loading...  " % frame, end="")
                time.sleep(delay)
                print("\r[%s]             " % frame, end="")
                time.sleep(delay)

        display_checkmark("\033[92mUninstall completed!\033[0m")
    except subprocess.CalledProcessError as e:
        print("Error:", e.output.decode().strip())

        
def start_serv():
    os.system("clear")
    print('\033[92m ^ ^\033[0m')
    print('\033[92m(\033[91mO,O\033[92m)\033[0m')
    print('\033[92m(   ) \033[93mRTT SERVICE\033[0m')
    print('\033[92m "-"\033[93m════════════════════════════════════\033[0m')
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print('\033[93mChoose what to do:\033[0m')
    print('1. \033[92mRestart SERVICE \033[0m')
    print('2. \033[93mStop SERVICE \033[0m')
    print('5. \033[94mBack to the main menu\033[0m')
    print("\033[93m╰───────────────────────────────────────╯\033[0m")

    while True:
        server_type = input('\033[38;5;205mEnter your choice Please: \033[0m')
        if server_type == '1':
            restart_serv()
            break
        elif server_type == '2':
            stop_serv()
            break
        elif server_type == '5':
            os.system("clear")
            main_menu()
            break
        else:
            print('Invalid choice.')

def display_status():
    services = {
        'iran': 'radkesvattunnel-iran.service',
        'kharej': 'radkesvattunnel-kharej.service'
    }

    print("\033[93m            ╔════════════════════════════════════════════╗\033[0m")
    print("\033[93m            ║           Radkesvattunnel Status           ║\033[0m")
    print("\033[93m            ╠════════════════════════════════════════════╣\033[0m")

    for service, service_name in services.items():
        try:
            status_output = os.popen(f"systemctl is-active {service_name}").read().strip()

            if status_output == "active":
                status = "\033[92m✓ Active     \033[0m"
            else:
                status = "\033[91m✘ Inactive   \033[0m"

            if service == 'iran':
                display_name = '\033[93mIran Server   \033[0m'
            elif service == 'kharej':
                display_name = '\033[93mKharej Service\033[0m'
            else:
                display_name = service

            print(f"           \033[93m ║\033[0m    {display_name}:   |    {status:<10}   \033[93m ║\033[0m")

        except OSError as e:
            print(f"Error retrieving status for {service}: {e}")
            continue

    print("\033[93m            ╚════════════════════════════════════════════╝\033[0m")
    
def restart_serv():
    os.system("clear")
    display_notification("\033[93mRestarting RTT..\033[0m")
    print("\033[93m╭─────────────────────────────────────────────╮\033[0m")

    try:
        subprocess.run("systemctl daemon-reload", shell=True)
        subprocess.run("systemctl restart radkesvattunnel-iran.service > /dev/null 2>&1", shell=True)
        time.sleep(1)
        subprocess.run("systemctl restart radkesvattunnel-kharej.service > /dev/null 2>&1", shell=True)
        time.sleep(1)


        print("Progress: ", end="")

        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        delay = 0.1
        duration = 3
        end_time = time.time() + duration

        while time.time() < end_time:
            for frame in frames:
                print("\r[%s] Loading...  " % frame, end="")
                time.sleep(delay)
                print("\r[%s]             " % frame, end="")
                time.sleep(delay)

        display_checkmark("\033[92mRestart completed!\033[0m")
    except subprocess.CalledProcessError as e:
        print("Error:", e.output.decode().strip())
        
def stop_serv():
    os.system("clear")
    display_notification("\033[93mStopping RTT..\033[0m")
    print("\033[93m╭─────────────────────────────────────────────╮\033[0m")

    try:
        subprocess.run("systemctl daemon-reload", shell=True)
        subprocess.run("systemctl stop radkesvattunnel-iran.service > /dev/null 2>&1", shell=True)
        time.sleep(1)
        subprocess.run("systemctl stop radkesvattunnel-kharej.service > /dev/null 2>&1", shell=True)
        time.sleep(1)


        print("Progress: ", end="")

        frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        delay = 0.1
        duration = 3
        end_time = time.time() + duration

        while time.time() < end_time:
            for frame in frames:
                print("\r[%s] Loading...  " % frame, end="")
                time.sleep(delay)
                print("\r[%s]             " % frame, end="")
                time.sleep(delay)

        display_checkmark("\033[92mService Stopped!\033[0m")
    except subprocess.CalledProcessError as e:
        print("Error:", e.output.decode().strip())
        
def install_hans():
    display_notification("\033[93mInstalling Hans ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_loading()
    subprocess.run(["echo", "'nameserver 8.8.8.8'", ">", "/etc/resolv.conf"], stderr=subprocess.DEVNULL, check=True, shell=True)

    ipv4_forward_status = subprocess.run(["sysctl", "net.ipv4.ip_forward"], capture_output=True, text=True)
    if "net.ipv4.ip_forward = 0" not in ipv4_forward_status.stdout:
        subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=1"])

    subprocess.run(["wget", "https://sourceforge.net/projects/hanstunnel/files/source/hans-1.1.tar.gz"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    subprocess.run(["tar", "-xzf", "hans-1.1.tar.gz"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    os.chdir("/root/hans-1.1")

    subprocess.run(["apt", "install", "-y", "make"], check=True)  
    subprocess.run(["apt", "install", "-y", "g++"], check=True)  
    subprocess.run(["make"], check=True)  

    display_checkmark("\033[92mHans installed successfully!\033[0m")

    os.remove("/root/hans-1.1.tar.gz")
	
def install_icmp():
    display_notification("\033[93mInstalling Icmptunnel ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_loading()

    subprocess.run(['sudo', 'tee', '/etc/resolv.conf'], input='nameserver 8.8.8.8\n', capture_output=True, text=True)


    ipv4_forward_status = subprocess.run(["sysctl", "net.ipv4.ip_forward"], capture_output=True, text=True)
    if "net.ipv4.ip_forward = 0" not in ipv4_forward_status.stdout:
        subprocess.run(["sudo", "sysctl", "-w", "net.ipv4.ip_forward=1"])


    ipv6_forward_status = subprocess.run(["sysctl", "net.ipv6.conf.all.forwarding"], capture_output=True, text=True)
    if "net.ipv6.conf.all.forwarding = 0" not in ipv6_forward_status.stdout:
        subprocess.run(["sudo", "sysctl", "-w", "net.ipv6.conf.all.forwarding=1"])


    if os.path.exists("/root/icmptunnel"):
        shutil.rmtree("/root/icmptunnel")


    clone_command = 'git clone https://github.com/jamesbarlow/icmptunnel.git icmptunnel'
    clone_result = os.system(clone_command)
    if clone_result != 0:
        print("Error: Failed to clone Repo.")
        return


    if os.path.exists("/root/icmptunnel"):

        os.chdir("/root/icmptunnel")


        subprocess.run(['sudo', 'apt', 'install', '-y', 'net-tools'], capture_output=True, text=True)
        subprocess.run(['sudo', 'apt', 'install', '-y', 'make'], capture_output=True, text=True)
        subprocess.run(['sudo', 'apt-get', 'install', '-y', 'libssl-dev'], capture_output=True, text=True)
        subprocess.run(['sudo', 'apt', 'install', '-y', 'g++'], capture_output=True, text=True)


        subprocess.run(['make'], capture_output=True, text=True)


        os.chdir("..")
    else:
        display_error("\033[91micmptunnel folder not found.\033[0m")
		
def rtt_ic_kharej():
    install_icmp()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring Kharej ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    subprocess.Popen('echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_all', shell=True, stderr=subprocess.PIPE).wait()

    if os.path.exists("/etc/icmp.sh"):
        os.remove("/etc/icmp.sh")

    with open("/etc/icmp.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write("/root/icmptunnel/icmptunnel -s -d\n")
        f.write("/sbin/ifconfig tun0 70.0.0.1 netmask 255.255.255.0\n")

    subprocess.run(["chmod", "700", "/etc/icmp.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)

    os.system("/bin/bash /etc/icmp.sh")

    cron_job_command = "@reboot root /bin/bash /etc/icmp.sh\n"
    with open("/etc/cron.d/icmp-kharej", "w") as f:
        f.write(cron_job_command)

    subprocess.call("crontab -u root /etc/cron.d/icmp-kharej", shell=True)

    display_checkmark("\033[92mCronjob added successfully!\033[0m")

def rtt_ic_iran():
    install_icmp()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring IRAN ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    subprocess.Popen('echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_all', shell=True, stderr=subprocess.PIPE).wait()

    os.chdir("/root/icmptunnel")

    server_ipv4 = input("\033[93mEnter \033[92mKharej\033[93m IPv4 address:\033[0m ")

    if os.path.exists("/etc/icmp-iran.sh"):
        os.remove("/etc/icmp-iran.sh")

    with open("/etc/icmp-iran.sh", "w") as f:
        f.write("#!/bin/bash\n")
        f.write(f"/root/icmptunnel/icmptunnel {server_ipv4} -d\n")
        f.write("/sbin/ifconfig tun0 70.0.0.2 netmask 255.255.255.0\n")

    subprocess.run(["chmod", "700", "/etc/icmp-iran.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)

    os.system("/bin/bash /etc/icmp-iran.sh")

    cron_job_command = "@reboot root /bin/bash /etc/icmp-iran.sh\n"
    with open("/etc/cron.d/icmp-iran", "w") as f:
        f.write(cron_job_command)

    subprocess.call("crontab -u root /etc/cron.d/icmp-iran", shell=True)

    display_checkmark("\033[92mCronjob added successfully!\033[0m")
    
def ic_rtt_menu():
    os.system("clear")
    print('\033[92m ^ ^\033[0m')
    print('\033[92m(\033[91mO,O\033[92m)\033[0m')
    print('\033[92m(   ) \033[93mIcmptunnel + RTT Menu\033[0m')
    print('\033[92m "-"\033[93m══════════════════════════\033[0m')
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print('\033[93mChoose what to do:\033[0m')
    print('1. \033[92mInstall RTT \033[0m')
    print('2. \033[93mSingle Port \033[0m')
    print('3. \033[96mMulti Port \033[0m')
    print('4. \033[94mBack to the main menu\033[0m')
    print("\033[93m╰───────────────────────────────────────╯\033[0m")

    while True:
        server_type = input('\033[38;5;205mEnter your choice Please: \033[0m')
        if server_type == '1':
            install_rtt()
            break
        elif server_type == '2':
            rtt_icmp_single()
            break
        elif server_type == '3':
            rtt_icmp_multi()
            break
        elif server_type == '4':
            os.system("clear")
            main_menu()
            break
        else:
            print('Invalid choice.')
			
			
def rtt_icmp_single():
    os.system("clear")
    print('\033[92m ^ ^\033[0m')
    print('\033[92m(\033[91mO,O\033[92m)\033[0m')
    print('\033[92m(   ) \033[93mIcmptunnel + RTT | Single Port\033[0m')
    print('\033[92m "-"\033[93m══════════════════════════\033[0m')
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print('\033[93mChoose what to do:\033[0m')
    print('1. \033[92mKharej  \033[0m')
    print('2. \033[93mIRAN  \033[0m')
    print('3. \033[94mBack to the previous menu\033[0m')
    print("\033[93m╰───────────────────────────────────────╯\033[0m")

    while True:
        server_type = input('\033[38;5;205mEnter your choice Please: \033[0m')
        if server_type == '1':
            kharej_rtt_single()
            break
        elif server_type == '2':
            iran_rtt_single()
            break
        elif server_type == '3':
            os.system("clear")
            ic_rtt_menu()
            break
        else:
            print('Invalid choice.')
			
def dl_and_install(url):
    subprocess.run(["sudo", "apt", "install", "zip", "-y"])

    filename = url.split('/')[-1]
    zip_path = os.path.join(os.getcwd(), filename)
    try:
        urllib.request.urlretrieve(url, zip_path)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.getcwd())
        os.remove(zip_path)
        display_checkmark("\033[92mInstallation Completed!\033[0m")
    except Exception as e:
        display_error(f"\033[91mAn error occurred during installation:\033[0m {str(e)}")

def chmod(file_path):
    try:
        subprocess.run(["chmod", "+x", file_path])

    except Exception as e:
        display_error(f"An error occurred while making {file_path} executable: {str(e)}")

def install_rtt():
    display_notification("\033[93mInstalling RTT ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    arch = os.uname().machine

    if arch in ['x86_64', 'amd64']:
        rtt_download_url = "https://github.com/radkesvat/ReverseTlsTunnel/releases/download/V6.7/v6.7_linux_amd64.zip"
    elif arch in ['aarch64', 'arm64']:
        rtt_download_url = "https://github.com/radkesvat/ReverseTlsTunnel/releases/download/V6.7/v6.7_linux_arm64.zip"
    else:
        display_error(f"Unsupported CPU architecture: {arch}")
        return

    dl_and_install(rtt_download_url)

    chmod("RTT")

def kharej_rtt_single():
    rtt_ic_kharej()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring Kharej ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    iran_lport = input("\033[93mEnter \033[92mIRAN\033[93m port (default: 443):\033[0m ") or "443"
    toport = input("\033[93mEnter \033[92mKharej\033[93m port :(Config Port)\033[0m ")
    sni = input("\033[93mEnter your desired \033[92mSNI\033[93m (default: github.com): \033[0m") or "github.com"
    terminate = input("\033[93mEnter the \033[92mRestart Service\033[93m value(default: 24):\033[0m ") or "24"

    service_content = f'''\
[Unit]
Description=Reverse TLS Tunnel


[Service]
Type=idle
User=root
WorkingDirectory=/root
ExecStart=/root/RTT --kharej --iran-ip:70.0.0.2 --iran-port:{iran_lport} --toip:127.0.0.1 --toport:{toport} --keep-ufw --password:azumichwan --sni:{sni} --terminate:{terminate}
Restart=always

[Install]
WantedBy=multi-user.target
'''

    with open('/etc/systemd/system/radkesvattunnel-kharej.service', 'w') as f:
        f.write(service_content)

    os.system('sudo systemctl daemon-reload')
    os.system('sudo systemctl start radkesvattunnel-kharej.service')
    os.system('sudo systemctl enable radkesvattunnel-kharej.service')
	
def iran_rtt_single():
    rtt_ic_iran()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring IRAN ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    iran_lport = input("\033[93mEnter \033[92mIRAN\033[93m port (default: 443):\033[0m ") or "443"
    iran_sni = input("\033[93mEnter your desired \033[92mSNI\033[93m (default: github.com):\033[0m ") or "github.com"
    iran_terminate = input("\033[93mEnter the \033[92mRestart Service\033[93m value(default: 24): \033[0m") or "24"

    iran_service_content = f'''\
[Unit]
Description=Reverse TLS Tunnel 'iran'


[Service]
Type=idle
User=root
WorkingDirectory=/root
ExecStart=/root/RTT --iran --lport:{iran_lport} --connection-age:15 --keep-ufw --log:0 --sni:{iran_sni} --password:azumichwan --terminate:{iran_terminate}
Restart=always

[Install]
WantedBy=multi-user.target
'''

    with open('/etc/systemd/system/radkesvattunnel-iran.service', 'w') as f:
        f.write(iran_service_content)

    os.system('sudo systemctl daemon-reload')
    os.system('sudo systemctl start radkesvattunnel-iran.service')
    os.system('sudo systemctl enable radkesvattunnel-iran.service')

def rtt_icmp_multi():
    os.system("clear")
    print('\033[92m ^ ^\033[0m')
    print('\033[92m(\033[91mO,O\033[92m)\033[0m')
    print('\033[92m(   ) \033[93mIcmptunnel + RTT | Multi Port\033[0m')
    print('\033[92m "-"\033[93m══════════════════════════\033[0m')
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print('\033[93mChoose what to do:\033[0m')
    print('1. \033[92mKharej  \033[0m')
    print('2. \033[93mIRAN  \033[0m')
    print('3. \033[94mBack to the previous menu\033[0m')
    print("\033[93m╰───────────────────────────────────────╯\033[0m")

    while True:
        server_type = input('\033[38;5;205mEnter your choice Please: \033[0m')
        if server_type == '1':
            kharej_rtt_multi()
            break
        elif server_type == '2':
            iran_rtt_multi()
            break
        elif server_type == '3':
            os.system("clear")
            ic_rtt_menu()
            break
        else:
            print('Invalid choice.')
			
def kharej_rtt_multi():
    rtt_ic_kharej()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring Kharej ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    iran_lport = input("\033[93mEnter \033[92mIRAN\033[93m port (default: 443):\033[0m ") or "443"
    sni = input("\033[93mEnter your desire \033[92mSNI\033[93m (default: github.com):\033[0m ") or "github.com"
    terminate = input("\033[93mEnter the \033[92mRestart Service\033[93m value:(default: 24)\033[0m ") or "24"

    service_content = f'''\
[Unit]
Description=Reverse TLS Tunnel


[Service]
Type=idle
User=root
WorkingDirectory=/root
ExecStart=/root/./RTT --kharej --iran-ip:70.0.0.2 --iran-port:{iran_lport} --toip:127.0.0.1 --toport:multiport --password:azumichwan --sni:{sni} --terminate:{terminate}
Restart=always

[Install]
WantedBy=multi-user.target
'''

    with open('/etc/systemd/system/radkesvattunnel-kharej.service', 'w') as f:
        f.write(service_content)

    os.system('sudo systemctl daemon-reload')
    os.system('sudo systemctl start radkesvattunnel-kharej.service')
    os.system('sudo systemctl enable radkesvattunnel-kharej.service')
    display_checkmark("\033[92mSetup completed successfully!\033[0m")
	
def iran_rtt_multi():
    rtt_ic_iran()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring IRAN ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    iran_sni = input("\033[93mEnter your desired \033[92mSNI\033[93m (default: github.com):\033[0m ") or "github.com"
    iran_terminate = input("\033[93mEnter the \033[92mRestart Service\033[93m value(default: 24): \033[0m") or "24"

    iran_service_content = f'''\
[Unit]
Description=Reverse TLS Tunnel 'iran'


[Service]
Type=idle
User=root
WorkingDirectory=/root
ExecStart=/root/./RTT --iran --lport:23-65535 --connection-age:15 --log:0 --sni:{iran_sni} --password:azumichwan --terminate:{iran_terminate}
Restart=always

[Install]
WantedBy=multi-user.target
'''

    with open('/etc/systemd/system/radkesvattunnel-iran.service', 'w') as f:
        f.write(iran_service_content)

    os.system('sudo systemctl daemon-reload')
    os.system('sudo systemctl start radkesvattunnel-iran.service')
    os.system('sudo systemctl enable radkesvattunnel-iran.service')
    display_checkmark("\033[92mSetup completed successfully!\033[0m")
	
def hns_rrtt_kharej():
    install_hans()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    subprocess.Popen('echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_all', shell=True, stderr=subprocess.PIPE).wait()
    hans_directory = "/root/hans-1.1"

    os.chdir(hans_directory)
    os.system(f"./hans -s 80.1.2.0 -p azumi86chwan -d icmp")

    subprocess.call(["crontab", "-r", "-u", "root"])

    hans_kharej_command = f"{hans_directory}/hans -s 80.1.2.0 -p azumi86chwan -d icmp"
    subprocess.run(["sed", "-i", f"/{hans_kharej_command}/d", "/etc/hans.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False)

    if os.path.exists("/etc/hans.sh"):
        os.remove("/etc/hans.sh")

    with open("/etc/hans.sh", "w") as f:
        f.write(f"{hans_kharej_command}\n")

    subprocess.run(["chmod", "700", "/etc/hans.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)

    cron_job_command = f"@reboot /bin/bash /etc/hans.sh\n"
    with open("/etc/cron.d/hans-kharej", "w") as f:
        f.write(cron_job_command)

    subprocess.call("crontab -u root /etc/cron.d/hans-kharej", shell=True)

    display_checkmark("\033[92mCronjob added successfully!\033[0m")
	
def hns_rrtt_iran():
    install_hans()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    subprocess.Popen('echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_all', shell=True, stderr=subprocess.PIPE).wait()
    server_ipv4 = input("\033[93mEnter \033[92mKharej\033[93m IPv4 address: \033[0m")

    os.chdir("/root/hans-1.1")
    os.system(f"./hans -c {server_ipv4} -p azumi86chwan -d icmp")

    os.system("ping -c 3 80.1.2.1")
    subprocess.call(["rm", "-f", "/etc/cron.d/hans"])

    hans_command = f"/root/hans-1.1/hans -c {server_ipv4} -p azumi86chwan -d icmp"
    subprocess.run(["sed", "-i", f"/{hans_command}/d", "/etc/hans.sh"], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False)

    if os.path.exists("/etc/hans.sh"):
        os.remove("/etc/hans.sh")

    with open("/etc/hans.sh", "w") as f:
        f.write(f"{hans_command}\n")

    cron_job_command = f"@reboot root /bin/bash /etc/hans.sh\n"
    with open("/etc/cron.d/hans-iran", "w") as f:
        f.write(cron_job_command)

    subprocess.call("crontab -u root /etc/cron.d/hans-iran", shell=True)

    display_checkmark("\033[92mCronjob added successfully!\033[0m")	

def hans_rtt_menu():
    os.system("clear")
    print('\033[92m ^ ^\033[0m')
    print('\033[92m(\033[91mO,O\033[92m)\033[0m')
    print('\033[92m(   ) \033[93mHans + RTT Menu\033[0m')
    print('\033[92m "-"\033[93m══════════════════════════\033[0m')
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print('\033[93mChoose what to do:\033[0m')
    print('1. \033[92mInstall RTT \033[0m')
    print('2. \033[93mSingle Port \033[0m')
    print('3. \033[96mMulti Port \033[0m')
    print('4. \033[94mBack to the main menu\033[0m')
    print("\033[93m╰───────────────────────────────────────╯\033[0m")

    while True:
        server_type = input('\033[38;5;205mEnter your choice Please: \033[0m')
        if server_type == '1':
            install_rtt()
            break
        elif server_type == '2':
            rtt_hans_single()
            break
        elif server_type == '3':
            rtt_hans_multi()
            break
        elif server_type == '4':
            os.system("clear")
            main_menu()
            break
        else:
            print('Invalid choice.')
			
def rtt_hans_single():
    os.system("clear")
    print('\033[92m ^ ^\033[0m')
    print('\033[92m(\033[91mO,O\033[92m)\033[0m')
    print('\033[92m(   ) \033[93mHans + RTT | Single Port\033[0m')
    print('\033[92m "-"\033[93m══════════════════════════\033[0m')
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print('\033[93mChoose what to do:\033[0m')
    print('1. \033[92mKharej  \033[0m')
    print('2. \033[93mIRAN  \033[0m')
    print('3. \033[94mBack to the previous menu\033[0m')
    print("\033[93m╰───────────────────────────────────────╯\033[0m")

    while True:
        server_type = input('\033[38;5;205mEnter your choice Please: \033[0m')
        if server_type == '1':
            kharej_rtthans_single()
            break
        elif server_type == '2':
            iran_rtthans_single()
            break
        elif server_type == '3':
            os.system("clear")
            hans_rtt_menu()
            break
        else:
            print('Invalid choice.')
			
def kharej_rtthans_single():
    hns_rrtt_kharej()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring Kharej ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    iran_lport = input("\033[93mEnter \033[92mIRAN\033[93m port (default: 443):\033[0m ") or "443"
    toport = input("\033[93mEnter \033[92mKharej\033[93m port:(Config port)\033[0m ")
    sni = input("\033[93mEnter your desired \033[92mSNI\033[93m (default: github.com): \033[0m") or "github.com"
    terminate = input("\033[93mEnter the \033[92mRestart Service\033[93m value:(default: 24)\033[0m ") or "24"

    service_content = f'''\
[Unit]
Description=Reverse TLS Tunnel


[Service]
Type=idle
User=root
WorkingDirectory=/root
ExecStart=/root/RTT --kharej --iran-ip:80.1.2.100 --iran-port:{iran_lport} --toip:127.0.0.1 --toport:{toport} --keep-ufw --password:azumichwan --sni:{sni} --terminate:{terminate}
Restart=always

[Install]
WantedBy=multi-user.target
'''

    with open('/etc/systemd/system/radkesvattunnel-kharej.service', 'w') as f:
        f.write(service_content)

    os.system('sudo systemctl daemon-reload')
    os.system('sudo systemctl start radkesvattunnel-kharej.service')
    os.system('sudo systemctl enable radkesvattunnel-kharej.service')
    display_checkmark("\033[92mSetup completed successfully!\033[0m")
	
def iran_rtthans_single():
    hns_rrtt_iran()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring IRAN ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    iran_lport = input("\033[93mEnter \033[92mIRAN\033[93m port (default: 443): \033[0m") or "443"
    iran_sni = input("\033[93mEnter your desired \033[92mSNI\033[93m (default: github.com):\033[0m ") or "github.com"
    iran_terminate = input("\033[93mEnter the \033[92mRestart Service\033[93m value:(default: 24)\033[0m ") or "24"

    iran_service_content = f'''\
[Unit]
Description=Reverse TLS Tunnel 'iran'


[Service]
Type=idle
User=root
WorkingDirectory=/root
ExecStart=/root/RTT --iran --lport:{iran_lport} --connection-age:15 --keep-ufw --log:0 --sni:{iran_sni} --password:azumichwan --terminate:{iran_terminate}
Restart=always

[Install]
WantedBy=multi-user.target
'''

    with open('/etc/systemd/system/radkesvattunnel-iran.service', 'w') as f:
        f.write(iran_service_content)

    os.system('sudo systemctl daemon-reload')
    os.system('sudo systemctl start radkesvattunnel-iran.service')
    os.system('sudo systemctl enable radkesvattunnel-iran.service')
    display_checkmark("\033[92mSetup completed successfully!\033[0m")

def rtt_hans_multi():
    os.system("clear")
    print('\033[92m ^ ^\033[0m')
    print('\033[92m(\033[91mO,O\033[92m)\033[0m')
    print('\033[92m(   ) \033[93mHans + RTT | Multi Port\033[0m')
    print('\033[92m "-"\033[93m══════════════════════════\033[0m')
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print('\033[93mChoose what to do:\033[0m')
    print('1. \033[92mKharej  \033[0m')
    print('2. \033[93mIRAN  \033[0m')
    print('3. \033[94mBack to the previous menu\033[0m')
    print("\033[93m╰───────────────────────────────────────╯\033[0m")

    while True:
        server_type = input('\033[38;5;205mEnter your choice Please: \033[0m')
        if server_type == '1':
            kharej_rtthans_multi()
            break
        elif server_type == '2':
            iran_rthans_mlti()
            break
        elif server_type == '3':
            os.system("clear")
            hans_rtt_menu()
            break
        else:
            print('Invalid choice.')
			
def kharej_rtthans_multi():
    hns_rrtt_kharej()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring Kharej ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    iran_lport = input("\033[93mEnter \033[92mIRAN\033[93m Port (default: 443): \033[0m") or "443"
    sni = input("\033[93mEnter your desired \033[92mSNI\033[93m (default: github.com): \033[0m") or "github.com"
    terminate = input("\033[93mEnter the \033[92mRestart Service\033[93m value:(default: 24) \033[0m") or "24"

    service_content = f'''\
[Unit]
Description=Reverse TLS Tunnel


[Service]
Type=idle
User=root
WorkingDirectory=/root
ExecStart=/root/./RTT --kharej --iran-ip:80.1.2.100 --iran-port:{iran_lport} --toip:127.0.0.1 --toport:multiport --password:azumichwan --sni:{sni} --terminate:{terminate}
Restart=always

[Install]
WantedBy=multi-user.target
'''

    with open('/etc/systemd/system/radkesvattunnel-kharej.service', 'w') as f:
        f.write(service_content)

    os.system('sudo systemctl daemon-reload')
    os.system('sudo systemctl start radkesvattunnel-kharej.service')
    os.system('sudo systemctl enable radkesvattunnel-kharej.service')
    display_checkmark("\033[92mSetup completed successfully!\033[0m")
	
def iran_rthans_mlti():
    hns_rrtt_iran()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring IRAN ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    iran_sni = input("\033[93mEnter your desired \033[92mSNI\033[93m (default: github.com): \033[0m") or "github.com"
    iran_terminate = input("\033[93mEnter the \033[92mRestart Service\033[93m value:(default: 24)\033[0m ") or "24"

    iran_service_content = f'''\
[Unit]
Description=Reverse TLS Tunnel 'iran'


[Service]
Type=idle
User=root
WorkingDirectory=/root
ExecStart=/root/./RTT --iran --lport:23-65535 --connection-age:15 --log:0 --sni:{iran_sni} --password:azumichwan --terminate:{iran_terminate}
Restart=always

[Install]
WantedBy=multi-user.target
'''

    with open('/etc/systemd/system/radkesvattunnel-iran.service', 'w') as f:
        f.write(iran_service_content)

    os.system('sudo systemctl daemon-reload')
    os.system('sudo systemctl start radkesvattunnel-iran.service')
    os.system('sudo systemctl enable radkesvattunnel-iran.service')
    display_checkmark("\033[92mSetup completed successfully!\033[0m")

def ic_rtt_udp():
    os.system("clear")
    print('\033[92m ^ ^\033[0m')
    print('\033[92m(\033[91mO,O\033[92m)\033[0m')
    print('\033[92m(   ) \033[93mIcmptunnel + RTT \033[92m[UDP]\033[93m Menu\033[0m')
    print('\033[92m "-"\033[93m══════════════════════════\033[0m')
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print('\033[93mChoose what to do:\033[0m')
    print('1. \033[92mInstall RTT \033[0m')
    print('2. \033[93mKharej \033[0m')
    print('3. \033[96mIRAN \033[0m')
    print('4. \033[94mBack to the main menu\033[0m')
    print("\033[93m╰───────────────────────────────────────╯\033[0m")

    while True:
        server_type = input('\033[38;5;205mEnter your choice Please: \033[0m')
        if server_type == '1':
            install_rtt()
            break
        elif server_type == '2':
            rtt_udp_kha()
            break
        elif server_type == '3':
            rtt_udp_ir()
            break
        elif server_type == '4':
            os.system("clear")
            main_menu()
            break
        else:
            print('Invalid choice.')
            
def rtt_udp_kha():
    rtt_ic_kharej()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring Kharej \033[92mUDP\033[93m...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    iran_lport = input("\033[93mEnter \033[92mIRAN\033[93m port (default: 443):\033[0m ") or "443"
    toport = input("\033[93mEnter \033[92mKharej\033[93m port :(Config Port) \033[0m")
    sni = input("\033[93mEnter your desired \033[92mSNI\033[93m (default: github.com):  \033[0m") or "github.com"
    terminate = input("\033[93mEnter the \033[92mRestart Service\033[93m value:(default: 24)  \033[0m") or "24"

    service_content = f'''\
[Unit]
Description=Reverse TLS Tunnel


[Service]
Type=idle
User=root
WorkingDirectory=/root
ExecStart=/root/RTT --kharej --iran-ip:70.0.0.2 --iran-port:{iran_lport} --toip:127.0.0.1 --toport:{toport} --keep-ufw --password:azumichwan --sni:{sni} --terminate:{terminate}
Restart=always

[Install]
WantedBy=multi-user.target
'''

    with open('/etc/systemd/system/radkesvattunnel-kharej.service', 'w') as f:
        f.write(service_content)

    os.system('sudo systemctl daemon-reload')
    os.system('sudo systemctl start radkesvattunnel-kharej.service')
    os.system('sudo systemctl enable radkesvattunnel-kharej.service')
	
def rtt_udp_ir():
    rtt_ic_iran()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring IRAN \033[92mUDP\033[93m ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    iran_lport = input("\033[93mEnter \033[92mIRAN\033[93m port (default: 443):  \033[0m") or "443"
    iran_sni = input("\033[93mEnter your desired \033[92mSNI\033[93m (default: github.com):  \033[0m") or "github.com"
    iran_terminate = input("\033[93mEnter the \033[92mRestart Service\033[93m value:(default: 24)  \033[0m") or "24"

    iran_service_content = f'''\
[Unit]
Description=Reverse TLS Tunnel 'iran'


[Service]
Type=idle
User=root
WorkingDirectory=/root
ExecStart=/root/RTT --iran --lport:{iran_lport} --accept-udp --connection-age:15 --keep-ufw --log:0 --sni:{iran_sni} --password:azumichwan --terminate:{iran_terminate}
Restart=always

[Install]
WantedBy=multi-user.target
'''

    with open('/etc/systemd/system/radkesvattunnel-iran.service', 'w') as f:
        f.write(iran_service_content)

    os.system('sudo systemctl daemon-reload')
    os.system('sudo systemctl start radkesvattunnel-iran.service')
    os.system('sudo systemctl enable radkesvattunnel-iran.service')
    
def hans_rtt_udp():
    os.system("clear")
    print('\033[92m ^ ^\033[0m')
    print('\033[92m(\033[91mO,O\033[92m)\033[0m')
    print('\033[92m(   ) \033[93mHans + RTT \033[92m[UDP]\033[93m Menu\033[0m')
    print('\033[92m "-"\033[93m══════════════════════════\033[0m')
    print("\033[93m╭───────────────────────────────────────╮\033[0m")
    print('\033[93mChoose what to do:\033[0m')
    print('1. \033[92mInstall RTT \033[0m')
    print('2. \033[93mKharej \033[0m')
    print('3. \033[96mIRAN \033[0m')
    print('4. \033[94mBack to the main menu\033[0m')
    print("\033[93m╰───────────────────────────────────────╯\033[0m")

    while True:
        server_type = input('\033[38;5;205mEnter your choice Please: \033[0m')
        if server_type == '1':
            install_rtt()
            break
        elif server_type == '2':
            hans_udp_kha()
            break
        elif server_type == '3':
            hans_udp_ir()
            break
        elif server_type == '4':
            os.system("clear")
            main_menu()
            break
        else:
            print('Invalid choice.')
            
def hans_udp_kha():
    hns_rrtt_kharej()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring Kharej \033[92mUDP\033[93m ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    iran_lport = input("\033[93mEnter \033[92mIRAN\033[93m port (default: 443): \033[0m") or "443"
    toport = input("\033[93mEnter \033[92mKharej\033[93m port:(Config port) \033[0m")
    sni = input("\033[93mEnter your desired \033[92mSNI\033[93m (default: github.com):\033[0m ") or "github.com"
    terminate = input("\033[93mEnter the \033[92mRestart Service\033[93m value:(default: 24) \033[0m") or "24"

    service_content = f'''\
[Unit]
Description=Reverse TLS Tunnel


[Service]
Type=idle
User=root
WorkingDirectory=/root
ExecStart=/root/RTT --kharej --iran-ip:80.1.2.100 --iran-port:{iran_lport} --toip:127.0.0.1 --toport:{toport} --keep-ufw --password:azumichwan --sni:{sni} --terminate:{terminate}
Restart=always

[Install]
WantedBy=multi-user.target
'''

    with open('/etc/systemd/system/radkesvattunnel-kharej.service', 'w') as f:
        f.write(service_content)

    os.system('sudo systemctl daemon-reload')
    os.system('sudo systemctl start radkesvattunnel-kharej.service')
    os.system('sudo systemctl enable radkesvattunnel-kharej.service')
    display_checkmark("\033[92mSetup completed successfully!\033[0m")
	
def hans_udp_ir():
    hns_rrtt_iran()
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    display_notification("\033[93mConfiguring IRAN \033[92mUDP\033[93m ...\033[0m")
    print("\033[93m──────────────────────────────────────────────────\033[0m")
    iran_lport = input("\033[93mEnter \033[92mIRAN\033[93m port (default: 443): \033[0m") or "443"
    iran_sni = input("\033[93mEnter your desired \033[92mSNI\033[93m (default: github.com): \033[0m") or "github.com"
    iran_terminate = input("\033[93mEnter the \033[92mRestart Service\033[93m value:(default: 24) \033[0m") or "24"

    iran_service_content = f'''\
[Unit]
Description=Reverse TLS Tunnel 'iran'


[Service]
Type=idle
User=root
WorkingDirectory=/root
ExecStart=/root/RTT --iran --lport:{iran_lport} --accept-udp --connection-age:15 --keep-ufw --log:0 --sni:{iran_sni} --password:azumichwan --terminate:{iran_terminate}
Restart=always

[Install]
WantedBy=multi-user.target
'''

    with open('/etc/systemd/system/radkesvattunnel-iran.service', 'w') as f:
        f.write(iran_service_content)

    os.system('sudo systemctl daemon-reload')
    os.system('sudo systemctl start radkesvattunnel-iran.service')
    os.system('sudo systemctl enable radkesvattunnel-iran.service')
    display_checkmark("\033[92mSetup completed successfully!\033[0m")
main_menu()
