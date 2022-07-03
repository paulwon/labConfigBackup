import os
import time
import requests
import configparser
from datetime import datetime
import csv
from xml.etree import ElementTree
import xmltodict
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import paramiko


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

configSaveDirectory = "/Users/zqwang/Library/CloudStorage/OneDrive-Personal/labConfigBackup/backupViaScript/"
# configSaveDirectory = "./"

appConfigFile = os.path.dirname(os.path.realpath(__file__)) + "/appConfig.csv"
configList = []
dataFormat = '%Y%m%d_%H%M%S'

def printMsgAndExit(msg):
    print(msg)
    print("Exiting ...")
    exit(1)


def readAppConfig():
    if not os.path.exists(appConfigFile):
        printMsgAndExit("The config file" +  appConfigFile + " does not exit") 
    print("Reading config from", appConfigFile)
    global configList
    with open(appConfigFile, newline='') as f:
        reader = csv.reader(f)
        configList = list(reader)
    # print(configList) 


def backupConfig():
    for configLine in configList:
        vendor = configLine[0].strip()
        # Skip the comment line (fist line with "#")
        if vendor[0] == "#":
            continue
        type = configLine[1].strip()
        systemName = configLine[2].strip()
        ip =  configLine[3].strip().split(":")[0]
        port = configLine[3].strip().split(":")[1]
        username = configLine[4].strip()
        password = configLine[5].strip()

        if vendor == "palo alto" and type == "api":
            paBackupConfig(systemName, ip, port, username, password)
        if vendor == "cisco" and type == "ssh":
            ciscoBackupConfig(systemName, ip, port, username, password)
        if vendor == "netgear" and type == "ssh":
            netgearBackupConfig(systemName, ip, port, username, password)
    print("Backup has been and and can be found at", configSaveDirectory )

# Backup for palo alto

def paBackupConfig(systemName, ip, port, username, password):
    print("Doing the config bakcup for", systemName)
    apiToken = paGetApiToken(ip, port, username, password)
    paGetbackupFile(systemName, ip, port, apiToken )

def paGetbackupFile(systemName, ip, port, apiToken):
    url = "https://{}:{}/api/?type=export&category=configuration&key={}".format(ip,port, apiToken)
    response = requests.get(url, verify=False)
    fileName = configSaveDirectory + systemName + "_"+ datetime.now().strftime(dataFormat) + ".xml"
    with open(fileName, "w") as f:
        f.write(response.text)
    f.close()

def paGetApiToken(ip, port, username, password):
    
    url =  "https://{}:{}/api/?type=keygen&user={}&password={}".format(ip, port, username, password)
    # print("Request the URL", url)
    response = requests.get(url, verify=False)
    dataDict = xmltodict.parse(response.content)
    # print(dataDict)
    apiKey = dataDict["response"]["result"]["key"]
    # print("apiKey is", apiKey)
    return apiKey

# Backup for Cisco

def ciscoBackupConfig(systemName, ip, port, username, password):
    
    print("Doing the config bakcup for", systemName)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('show run')
    fileName = configSaveDirectory + systemName + "_"+ datetime.now().strftime(dataFormat) + ".txt"
    list = stdout.readlines()
    outfile = open(fileName, "w")
    for char in list:
        outfile.write(char)
    ssh.close()
    outfile.close()

# Backup for netgear
def netgearBackupConfig(systemName, ip, port, username, password):
    print("Doing the config bakcup for", systemName)
    fileName = configSaveDirectory + systemName + "_"+ datetime.now().strftime(dataFormat) + ".txt"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip, username=username, password=password, port=port)
    chan = ssh.invoke_shell()
    time.sleep(2)
    chan.send('enable\n')
    time.sleep(1)
    chan.send('term len 0\n')
    time.sleep(1)
    chan.send('sh run\n')
    time.sleep(5)
    output = chan.recv(999999)
    f1 = open(fileName, 'a')
    f1.write(output.decode("utf-8") )
    f1.close()
    ssh.close()

if __name__ == "__main__":
    readAppConfig()
    backupConfig()
