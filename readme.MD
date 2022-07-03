# Python script to backup runnning config
## Support method
- API (for Palo Alto)
- SSH 
## Supported vendor
- Palo Also
- Cisco
- Netgear

## Usage
### Applicaiton configuraiton file
A file named "appConfig.csv" with the following format needs to placed under the same directory where the script exist.

    # vender, method, systemName, ip, username, password
    palo alto, api, pa500, 192.168.1.1:443,admin, password
    cisco, ssh, site2cisco, 192.168.1.2:1317,adin, password
    netgear, ssh, site3netgear,192.168.1.3:1303,admin,password

