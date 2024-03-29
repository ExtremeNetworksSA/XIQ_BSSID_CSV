#!/usr/bin/python3
import time
import datetime
import sys
import getpass
import os
import argparse
import textfsm
import logging
import pandas as pd
from app.xiq_api import XIQ
from app.bssid_logger import logger
logger = logging.getLogger('BSSID_CSV.Main')


PATH = os.path.dirname(os.path.abspath(__file__))
os.environ["NET_TEXTFSM"]='{}/templates/'.format(PATH)

outputFile = 'AP_bssids.csv'

cmd = 'show interface'
templateraw = 'hiveos_show_interface.template'

# Git Shell Coloring - https://gist.github.com/vratiu/9780109
RED   = "\033[1;31m"  
BLUE  = "\033[1;34m"
GREEN = "\033[0;32m"
YELLOW = "\033[0;33m"
RESET = "\033[0;0m"


parser = argparse.ArgumentParser()
parser.add_argument('--external',action="store_true", help="Optional - adds External Account selection, to collect bssid's on external VIQ")
args = parser.parse_args()

filetype = 'name'

selection = 0
device_name = ''
building_name = ''

def yesNoLoop(question):
    validResponse = False
    while validResponse != True:
        response = input(f"{question} (y/n) ").lower()
        if response =='n' or response == 'no':
            response = 'n'
            validResponse = True
        elif response == 'y' or response == 'yes':
            response = 'y'
            validResponse = True
        elif response == 'q' or response == 'quit':
            sys.stdout.write(RED)
            sys.stdout.write("script is exiting....\n")
            sys.stdout.write(RESET)
            raise SystemExit
    return response

def main():
    msg = 'AP NAME, INTERFACE, STATE, BSSID, SSID\n'

    #TODO - Prompt for all devices, list of devices from file, or single device.
    validResponse = False
    while not validResponse:
        print("Please choose from the options below:")
        print("1. Collect bssids from a list of AP names in a text file. (AP name on each line)")
        print("2. Collect the bssid for a single device by name.")
        print("3. Collect bssids for all devices in a building.")
        print("4. Collect bssids for all devices in VIQ.")
       
        selection = input("Please enter 1 - 4: ")
        try:
            selection = int(selection)
        except:
            sys.stdout.write(YELLOW)
            sys.stdout.write("Please enter a valid response!!\n")
            sys.stdout.write(RESET)
            continue
        if selection == 1:
            validResponse = True
            ## Device Files
            filename = str(input("Please enter the file with the list of devices: ")).strip()
            filename = filename.replace("\\ ", " ")
            filename = filename.replace("'", "")
            try:
                with open(filename, 'r') as f:
                    device_list = f.read().splitlines()
            except FileNotFoundError as e:
                logger.warning(e)
                print("script is exiting")
                raise SystemExit
        elif selection == 2:
            validResponse = True
            device_name = input("Enter the name of the device you would like to collect: ")
        elif selection == 3:
            validResponse = True
            building_name = input("Enter the name of the building you would like to collect devices from: ")
        elif selection == 4:
            validResponse = True
        else:
            sys.stdout.write(YELLOW)
            sys.stdout.write(f"{selection} is not a valid response between 1-4.\n")
            sys.stdout.write("Please enter a valid response!!\n")
            sys.stdout.write(RESET)


    
    print("Enter your XIQ login credentials")
    username = input("Email: ")
    password = getpass.getpass("Password: ")
    try:
        x = XIQ(user_name=username,password = password)
    except ValueError as e:
        print("script is exiting...")
        raise SystemExit
    except:
        print("Unknown Error connecting to XIQ.")
        print("script is exiting...")
        raise SystemExit
    
    #OPTIONAL - use externally managed XIQ account
    if args.external:
        accounts, viqName = x.selectManagedAccount()
        if accounts == 1:
            validResponse = False
            while validResponse != True:
                response = yesNoLoop("No External accounts found. Would you like to import data to your network?")
                if response == 'y':
                    validResponse = True
                elif response =='n':
                    sys.stdout.write(RED)
                    sys.stdout.write("script is exiting....\n")
                    sys.stdout.write(RESET)
                    raise SystemExit
        elif accounts:
            validResponse = False
            while validResponse != True:
                print("\nWhich VIQ would you like to collect BSSIDs from?")
                accounts_df = pd.DataFrame(accounts)
                count = 0
                for df_id, viq_info in accounts_df.iterrows():
                    print(f"   {df_id}. {viq_info['name']}")
                    count = df_id
                print(f"   {count+1}. {viqName} (This is Your main account)\n")
                selection = input(f"Please enter 0 - {count+1}: ")
                try:
                    selection = int(selection)
                except:
                    sys.stdout.write(YELLOW)
                    sys.stdout.write("Please enter a valid response!!")
                    sys.stdout.write(RESET)
                    continue
                if 0 <= selection <= count+1:
                    validResponse = True
                    if selection != count+1:
                        newViqID = (accounts_df.loc[int(selection),'id'])
                        newViqName = (accounts_df.loc[int(selection),'name'])
                        x.switchAccount(newViqID, newViqName)
    if selection == 1:
        sizeofbatch = 50
        for i in range(0, len(device_list), sizeofbatch):
            batch = device_list[i:i+sizeofbatch]
            if filetype == 'name':
                rawDeviceData = x.collectDevices(pageSize=sizeofbatch,hostname=batch)
                if rawDeviceData:
                    device_df = pd.DataFrame(rawDeviceData)
                    device_df.set_index('id',inplace=True)
                id_list = [sub['id'] for sub in rawDeviceData ]
    elif selection == 2:
        rawDeviceData = x.collectDevices(pageSize=100,hostname=[device_name])
        if rawDeviceData:
            device_df = pd.DataFrame(rawDeviceData)
            device_df.set_index('id',inplace=True)
        id_list = [sub['id'] for sub in rawDeviceData ]
    elif selection == 3:
        floor_ids = x.getFloorIds(building_name)  
        rawDeviceData = x.collectDevices(pageSize=100,location_id=floor_ids)
        if rawDeviceData:
            device_df = pd.DataFrame(rawDeviceData)
            device_df.set_index('id',inplace=True)
        id_list = [sub['id'] for sub in rawDeviceData ]
    elif selection == 4:
        rawDeviceData = x.collectDevices(pageSize=100)
        if rawDeviceData:
            device_df = pd.DataFrame(rawDeviceData)
            device_df.set_index('id',inplace=True)
        id_list = [sub['id'] for sub in rawDeviceData ]
    if id_list:
        commands = ["show interface"]
        rawData = x.sendCLI(id_list, commands)
        for device_id in rawData['device_cli_outputs']:
                output = rawData['device_cli_outputs'][device_id][0]['output']
                devicename = device_df.loc[int(device_id),'hostname']
                with open('{}/templates/{}'.format(PATH,templateraw), 'r') as f:
                    test_template = textfsm.TextFSM(f)
                test_config = test_template.ParseText(output)
                parsed = [dict(zip(test_template.header, row)) for row in test_config]
                if len(parsed) == 0:
                    logger.warning(f'Device {devicename} returned response: "{output}". This device will be skipped.')
                for dv in parsed:
                    if 'Wifi' in dv["NAME"]:
                        msg += f'{devicename},{dv["NAME"]},{dv["STATE"]},{dv["MAC"]},{dv["SSID"]}\n'
    else:
        logger.warning("No devices were found!")               
        
    with open("{}/{}".format(PATH,outputFile), 'w') as f:
        f.write(msg)
    print("Completed. Please look at {} for results".format(outputFile))

if __name__ == '__main__':
    main()




    