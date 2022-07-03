# Lab Configuration Backup
Python script to backup runnning config for mutiple network devices (switch, firewall, etc) provided as a csv file. 
## Support backup methods
- API (for Palo Alto)
- SSH 
## Supported vendors
- Palo Alto
- Cisco
- Netgear

## Usage
### Applicaiton configuraiton file
A file named "appConfig.csv" with the following format needs to be placed under the same directory where the script runs.

    # vender, method, systemName, ip, username, password
    palo alto, api, pa500, 192.168.1.1:443,admin, password
    cisco, ssh, site2cisco, 192.168.1.2:1317,adin, password
    netgear, ssh, site3netgear,192.168.1.3:1303,admin,password

