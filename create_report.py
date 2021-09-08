import os
import time
import json
import shutil
import argparse
import getpass

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

## CONSTANT DEFINITION
url = "https://danam.cats.uni-heidelberg.de/report/"

username = getpass.getuser()

if os.name == "posix": #LINUX
    download = "/home/{}/Downloads/".format(username)   
    save_folder = "/home/{}/Documents/DANAM Reports/".format(username)   

else: #WINDOWS
    download = "C:\\Users\\{}\\Downloads\\".format(username) 
    save_folder = "C:\\Users\\{}\\Documents\\DANAM Reports\\".format(username) 


'''
read monument URL id from metadata csv
'''
def get_url_from_csv(csv):
    ids = []
    firstline = True
    
    with open(csv, 'r', encoding="utf8") as file:
        for line in file:
            line = file.readline()
            
            #skip first line (headers)
            if firstline:
                firstline = False

            else:
                #try to get the id (2nd element from the back)
                try:
                    id = line.split(";")[-2].replace('\"', '')
                    ids.append(id)
                except:
                    continue

    #turn ids array into set to remove duplicates
    ids = set(ids)
    return ids

'''
read monument URL id from a simple txt file (one id per line). 
IDs can be commented as follows:

017a4a8f-b183-4e57-9ff9-54ae1145378f #LAL1870
60a8a8e0-e4e8-11e9-b125-0242ac130002 #LAL4250
cfc0099e-f15d-4c3e-8d8f-e048222f7956 #KIR0020

IDs can be commented python-wise with #

'''
def get_url_from_txt(textfile):
    ids = []

    with open(textfile, 'r', encoding="utf-8") as file:
        for line in file:
            if line[0] == "#":
                continue
            id = line.split(" ")[0]
            ids.append(id)

    return set(ids)

'''
start chromedriver with setting for printing to pdf
'''
def chromedriver_init():

    if os.name == "posix":
        CHROMEDRIVER_PATH = './chromedriver'
    else:
        CHROMEDRIVER_PATH = './chromedriver.exe'
        
    options = Options()
    appState = {
        "recentDestinations": [
            {
                "id": "Save as PDF",
                "origin": "local",
                "account": "",
            }
        ],
        "selectedDestinationId": "Save as PDF",
        "version": 2
        }

    profile = {'printing.print_preview_sticky_settings.appState': json.dumps(appState)}
    #profile = {'printing.print_preview_sticky_settings.appState':json.dumps(appState),'download.default_directory':downloadPath}
    options.add_experimental_option('prefs', profile)
    options.add_argument('--kiosk-printing')

    driver = webdriver.Chrome(options=options, executable_path=CHROMEDRIVER_PATH)
    return driver

'''
get reports from id
'''
def get_reports(ids, driver):
    for id in ids:
        try:
            driver.get(url+id)
            print(driver.title + " loaded.")
            time.sleep(10)
            driver.execute_script('window.print();')
            print(driver.title + " downloaded.")
            filename = driver.title + ".pdf"

            shutil.move(download+filename, save_folder+filename)

        except:
            continue

    driver.quit()

if __name__ == "__main__":

    argparser = argparse.ArgumentParser(description="Get DANAM report as a PDF using automated Chrome")

    argparser.add_argument("-csv", required=False, type=str, help="metadata csv to read URL id from")
    argparser.add_argument("-txt", required=False, type=str, help="textfile to read URL id from")
    argparser.add_argument("-save_folder", required=False, type=str, help="save folder, if not specified, saves at ./report")
    
    args = argparser.parse_args()


    if args.save_folder != None:
        save_folder = args.save_folder

    if not os.path.isdir(save_folder):
        os.mkdir(save_folder)

    if args.csv != None:
        print("Reading URL from "+args.csv)
        ids = get_url_from_csv(args.csv)
    
    elif args.txt != None:
        print("Reading URL from "+args.txt)
        ids = get_url_from_txt(args.txt)

    else:
        print("No input given! Please give a csv or txt file.\nType -h for help\n")
        ids = []

    if len(ids) > 0:
        print("Default Downloads folder: " + download)
        print("Reports will be saved to: " + save_folder)
        print("Starting Chrome...")
        driver = chromedriver_init()
        print("Chrome started.")
        get_reports(ids, driver)