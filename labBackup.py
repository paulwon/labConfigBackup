import configparser
import os
import time
import requests
from datetime import datetime
import csv
import xmltodict
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import paramiko


requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

devicesListFile = os.path.dirname(os.path.realpath(__file__)) + "/devicesList.csv"
devicesList = []
dataFormat = '%Y%m%d_%H%M%S'

def printMsgAndExit(msg):
    print(msg)
    print("Exiting ...")
    exit(1)


def readAppConfig():
    '''
    Read the devices list in the csv format
    '''
    if not os.path.exists(devicesListFile):
        printMsgAndExit("The config file" +  devicesListFile + " does not exit") 
    print("Reading config from", devicesListFile)
    global devicesList
    with open(devicesListFile, newline='') as f:
        reader = csv.reader(f)
        devicesList = list(reader)
    # print(configList) 


def backupConfig():
    '''
    Loop through the csv file to do backup for each device
    '''
    for configLine in devicesList:
        vendor = configLine[0].strip()
        # Skip the comment line (first line with "#")
        if vendor[0] == "#":
            continue
        os = configLine[1].strip()
        type = configLine[2].strip()
        systemName = configLine[3].strip()
        ip =  configLine[4].strip().split(":")[0]
        port = configLine[4].strip().split(":")[1]
        username = configLine[5].strip()
        password = configLine[6].strip()

        if vendor.lower() == "palo alto" and os.lower() == "pan-os" and type.lower() == "api":
            paBackupConfig(systemName, ip, port, username, password)
        if vendor.lower() == "cisco" and os.lower() == "ios"  and type.lower() == "ssh":
            ciscoBackupConfig(systemName, ip, port, username, password)
        if vendor.lower() == "netgear" and os.lower() == "prosafe" and type.lower() == "ssh":
            netgearBackupConfig(systemName, ip, port, username, password)
        if vendor.lower() == "extreme networks" and os.lower() == "exos" and type.lower() == "ssh":
            exosBackupConfig(systemName, ip, port, username, password)
    print("Backup has been and and can be found at", configSaveDirectory )


def paBackupConfig(systemName, ip, port, username, password):
    '''
    Backup for palo alto pan-os devices
    '''
    print("Doing the config bakcup for", systemName)
    apiToken = paGetApiToken(ip, port, username, password)
    paGetbackupFile(systemName, ip, port, apiToken )

def paGetApiToken(ip, port, username, password):
    '''
    Get the api key first before doing the API call against palo alto devices 
    '''
    url =  "https://{}:{}/api/?type=keygen&user={}&password={}".format(ip, port, username, password)
    # print("Request the URL", url)
    response = requests.get(url, verify=False)
    dataDict = xmltodict.parse(response.content)
    # print(dataDict)
    apiKey = dataDict["response"]["result"]["key"]
    # print("apiKey is", apiKey)
    return apiKey


def paGetbackupFile(systemName, ip, port, apiToken):
    '''
    Get palo alto backup xml file via API call
    '''
    url = "https://{}:{}/api/?type=export&category=configuration&key={}".format(ip,port, apiToken)
    response = requests.get(url, verify=False)
    fileName = configSaveDirectory + systemName + "_"+ datetime.now().strftime(dataFormat) + ".xml"
    with open(fileName, "w") as f:
        f.write(response.text)
    f.close()



def ciscoBackupConfig(systemName, ip, port, username, password):
    '''
    Backup for Cisco
    '''
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

def netgearBackupConfig(systemName, ip, port, username, password):
    '''
    Backup for netgear
    '''
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
    file = open(fileName, 'a')
    file.write(output.decode("utf-8") )
    file.close()
    ssh.close()


def exosBackupConfig(systemName, ip, port, username, password):
    '''
    Backup for Extreme EXOS
    '''
    print("Doing the config bakcup for", systemName)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=ip, username=username, password=password, port=port)
    stdin, stdout, stderr = ssh.exec_command('show config')
    fileName = configSaveDirectory + systemName + "_"+ datetime.now().strftime(dataFormat) + ".txt"
    list = stdout.readlines()
    outfile = open(fileName, "w")
    for char in list:
        outfile.write(char)
    ssh.close()
    outfile.close()

if __name__ == "__main__":
    if os.path.exists(os.path.dirname(os.path.realpath(__file__)) + "/appConfig.ini"):
        print("Reading the config save dirctory from the app configuraton file 'appConfig.ini")
        config = configparser.ConfigParser()
        config.read(os.path.dirname(os.path.realpath(__file__)) + "/appConfig.ini")
        configSaveDirectory = config.get("appConfig", "configSaveDirectory").strip()
        
    else:
        print("Config files will be saved to the same direcotry where the script runs because the file 'appConfig.ini' does not exits")
        configSaveDirectory = "./"
        
    readAppConfig()
    backupConfig()
