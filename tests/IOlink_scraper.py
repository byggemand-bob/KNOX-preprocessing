from bs4 import BeautifulSoup as soup
from urllib.request import urlopen as uReq
import requests

FOLDER = 'test/'

def main():
    # read all links
    file1 = open('ioilinks.txt', 'r') 
    Lines = file1.readlines() 

    # set count
    count = 1

    for line in Lines: 
        # print count and url
        print("Line{}: {}".format(count, line.strip())) 
        count +=1

        # get a file name
        productName = findfilename(line)

        if '.pdf' in productName:
    
            with open(FOLDER + productName, 'wb') as file:
                response = requests.get(line)
                file.write(response.content)
        elif '.zip' in line:
            with open(FOLDER + productName, 'wb') as file:
                response = requests.get(line)
                file.write(response.content)
        else:
            print('unknown file type: ' + line)
            break;

def findNextPage(page_soup):
    try:
        pages = page_soup.findAll("div",{"class":"sp_pagination section"})
        allPages = pages[0].div.ul.findAll("li")
        return 'https://www.grundfos.com' + allPages[len(allPages)-1].a['href']
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