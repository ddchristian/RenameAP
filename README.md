# Update Cisco AP Name
script version 0.1 <br>
date: 10/10/2022 <br>
author: Demetrius Christian <br>
email: dchristi@cisco.com <br>

Script provided to rename AP names running command from WLC. <br>
It reads the old AP name and new AP names from excel sheet. The
script can be used on both AireOS as well as IOS XE controllers.

Tested on: <br>
5520 Controller with 8.10 code <br>
Cat 9800 Controller with  17.03.04c code <br>
Python 3.1 on MAC OSX 11.6.8pandas==1.5.0 <br>
netmiko==4.1.2 <br>
numpy==1.23.3 <br>
openpyxl==3.0.10 <br>
pandas==1.5.0 <br>
paramiko==2.11.0 <br>

Ensure openpyxl library is imported for pandas excel engine handling. <br>
Script creates Current_AP.xlsx file when retrieving AP names from WLC. <br>
Script reads rename_ap.xlsx.xlsx file by default for AP name change.