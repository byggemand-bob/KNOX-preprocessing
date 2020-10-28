from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import requests
import os

FOLDER = 'PDF/'
DOMAIN = 'https://www.grundfos.com'

def main():
    # read all links
    file1 = open('ioilinks.txt', 'r') 
    Lines = file1.readlines() 

    # check if a folder for pdf is made
    cwd = os.getcwd()
    if not os.path.exists(os.path.join(cwd,FOLDER)):
        os.mkdir(os.path.join(cwd,FOLDER))
        

    # set count
    count = 1

    for line in Lines: 
        # print count and url
        print("Line{}: {}".format(count, line.strip())) 
        count +=1

        # get a file name
        productName = findfilename(line.rstrip("\n"))
        
        with open(FOLDER + productName, 'wb') as file:
                response = requests.get(line)
                file.write(response.content)

def findNextPage(page_soup):
    try:
        pages = page_soup.findAll("div",{"class":"sp_pagination section"})
        allPages = pages[0].div.ul.findAll("li")
        return DOMAIN + allPages[len(allPages)-1].a['href']
    except:
        return None

def parseURL(url):
    #opening op connection, grabbing the page
    uClient = uReq(url)
    page_html = uClient.read()
    uClient.close()

    #html parsing
    return soup(page_html, "html.parser")

def findfilename(string):
    dirs = string.split('/')
    
    return dirs[len(dirs)-1]
            
main()
