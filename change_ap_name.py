"""
script version 0.1
date: 10/10/2022
author: Demetrius Christian
email: dchristi@cisco.com

Script provided to rename AP names running command from WLC.
Reads old AP name and new AP name from excel sheet.
Script can be used on both AireOS as well as IOS XE controllers.

Tested on:
5520 Controller with 8.10 code
Cat 9800 Controller with  17.03.04c code
Python 3.1 on MAC OSX 11.6.8pandas==1.5.0
netmiko==4.1.2
numpy==1.23.3
openpyxl==3.0.10
pandas==1.5.0
paramiko==2.11.0

Ensure openpyxl library is imported for pandas excel engine handling.
Script creates Current_AP.xlsx file when retrieving AP names from WLC.
Script reads rename_ap.xlsx.xlsx file by default for AP name change.
"""

import re
from datetime import datetime
import getpass
import pandas as pd
import numpy as np
import openpyxl
from netmiko import ConnectHandler
from netmiko import NetMikoTimeoutException
from netmiko import NetmikoAuthenticationException as AuthenticationException
from paramiko.ssh_exception import SSHException


def rename_ap(old_name, new_name):

    if wlc == 'iosxe':
        command = 'ap name {} name {}'.format(old_name, new_name )
    elif wlc == 'aireos':
        command = 'config ap name {} {}'.format(new_name, old_name)
    output = net_connect.send_command(command)
    print(output)

    if 'invalid' or '% Error:' in output.strip():
        error_msg = 'AP is not connected to network.'
        print(error_msg)
        return error_msg

    return 'yes'


def get_data():

    print('Default excel file: rename_ap.xlsx')
    ap_file = input('Enter new file name or hit return to accept the default: ')
    if ap_file == '':
        ap_file = 'rename_ap.xlsx'

    print('Default worksheet name: Sheet1')
    ap_sheet = input('Enter new excel Sheet name or hit return to accept the default: ')
    if ap_sheet == '':
        ap_sheet = 'Sheet1'
    print('\n')
    df = pd.read_excel(ap_file, sheet_name=ap_sheet, engine='openpyxl')
    df = df.replace(np.nan, '', regex=True)
    total_rows = len(df['Current AP Name'])
    print('There are {} APs to process from file: {}, sheet: {}'.format(total_rows, ap_file, ap_sheet))

    ap_data = []
    for index, row in df.iterrows():
        ap_row = {}
        ap_row['row'] = index
        ap_row['old_name'] = row['Current AP Name'].replace(' ', '')
        ap_row['new_name'] = row['New AP Name'].replace(' ', '')
        if str(ap_row['new_name']) == '':
            ap_row['clean_data'] = 'Data Error: New AP Name not defined'
        elif ap_row['old_name'] == ap_row['new_name']:
            ap_row['clean_data'] = 'Data Error: Current AP Name and New AP Name is the same'
        elif ap_row['old_name'] == '':
            ap_row['clean_data'] = 'Data Error: Current AP Name not defined'
        else :
            ap_row['clean_data'] = 'yes'

        ap_data.append(ap_row)

    return ap_data, total_rows


def change_ap():

    ap_data, total_ap = get_data()

    for ap in range(len(ap_data)):
        row = ap_data[ap]['row'] + 2
        old_name = ap_data[ap]['old_name']
        new_name = ap_data[ap]['new_name']
        clean_data = ap_data[ap]['clean_data']

        if not clean_data == 'yes':
            print('{}: Error with row - {}'.format(row, clean_data))
            continue

        print('{}: Processing {}  {}'.format(row, old_name, new_name))

        change_state = rename_ap(old_name, new_name)
        if not change_state == 'yes':
            ap_data[ap]['clean_data'] = change_state

    print('\n')

    return ap_data


def get_ap_names():
    command = 'show ap summary'
    output = net_connect.send_command(command)
    print(output)
    reg_ex_pattern = r'(\S{1,64})\s+[0-9]\s{6}[-A-Z0-9]+\s+([a-zA-Z0-9:.]+)'
    ap_details = re.findall(reg_ex_pattern, output)
    total_ap = len(ap_details)
    print("Total number of AP's currently connected to WLC: {}\n".format(total_ap))

    ap_name = []
    for ap in ap_details:
        ap_name.append(ap[0])
    #print(ap_name)
    df = pd.DataFrame(ap_name, columns=['Current AP Name'])
    #print(df)
    df.to_excel('Current_AP.xlsx', index=False)
    print('AP list exported to excel: Current_AP.xlsx')
    print("Add additional column to excel with name 'New AP Name' and add new AP names.")
    print('Rename excel to the default: rename_ap.xlsx or other suitable name to be used for Change AP routine.')

    return


if __name__ == '__main__':

    wlc_ip = input('WLC IP Address: ')
    ssh_userId = input('WLC Username: ')
    ssh_passwd = getpass.getpass('WLC ssh password: ')

    start_time = datetime.now()
    print(start_time)
    print('Starting connection to WLC: {} with userid: {}'.format(wlc_ip, ssh_userId))

    device_ssh = {
        'device_type': 'cisco_wlc_ssh',
        'ip': wlc_ip,
        'username': ssh_userId,
        'password': ssh_passwd,
        'port' : 22,
    }

    try:
        net_connect = ConnectHandler(**device_ssh)
        output = net_connect.find_prompt()
    except (AuthenticationException):
        print ("SSH Authentication failure: " + wlc_ip )
        exit()
    except (NetMikoTimeoutException):
        print ("SSH Timeout to device: " + wlc_ip )
        exit()
    except (EOFError):
        print ("End of file while attempting device " + wlc_ip )
        exit()
    except (SSHException):
        print ("SSH Issue. Are you sure SSH is enabled? " + wlc_ip )
        exit()
    except Exception as unknown_error:
        print ("Some other error: " + str(unknown_error) + wlc_ip )
        exit()

    if output != None and '#' in output:
        wlc = 'iosxe'
    elif output != None and '>' in output:
        wlc = 'aireos'

    print('Connected to {} WLC: {} at: {}'.format(wlc, output, wlc_ip))

    print('\nSelect script ofptions from below.')
    print("A: Generate an Excel with the names of the Current AP's")
    print("B: Change AP names using an Excel sheet")
    selection = input('Select option: ')
    selection = selection.lower()

    if selection == 'a':
        get_ap_names()
    elif selection == 'b':
        results = change_ap()

        success_adds = 0
        failed_adds = 0
        print('Summarizing failed rows:')
        for index in range(len(results)):
            row = results[index]['row'] + 2
            clean_data = results[index]['clean_data']
            if not clean_data == 'yes':
                failed_adds += 1
                print('{}: Error with row - {}'.format(row, clean_data))
            else:
                success_adds += 1
        print('\n')
        print('Total failed AP name changes: ', failed_adds)
        print('Succesfull AP name changes: ', success_adds)
    else:
        print('Incorrect selection chosen. Exiting script')
        exit()

    end_time = datetime.now()
    print('Total run time was: {}'.format(end_time - start_time))


