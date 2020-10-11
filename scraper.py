'''
MIT License

Copyright (c) 2020 MoranARM

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''
import requests
import time
from bs4 import BeautifulSoup
from sys import argv
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
import os
from os.path import exists
from selenium.common.exceptions import NoSuchElementException

# Mode options are 0 for grab links and download files, 1 for grab links only, and 2 for download only
site = argv[1]
pause = 2 if len(argv)<3 else argv[2] # increase if page does not load images fast enough
mode = 0 if len(argv)<4 else argv[3] # sets default mode to 0
URL = ""+site
subdirectory = (URL if '?s=cl' not in URL else URL[:-5]).split('/')[-1]
print(subdirectory)
driver = webdriver.Firefox() # Requires selenium webdriver
file_names = []  # a list to store the names that will be used to grab each image
vid_links = []

def set_variables(url): # Resets the gloabl variables used for each user
    global URL, subdirectory, file_names, vid_links # Allows the function to reset global variables
    URL = ""+url
    subdirectory = (URL if '?s=cl' not in URL else URL[:-5]).split('/')[-1]
    file_names = []
    vid_links = []

def new_soup(url):  # function to create new html objects from bs
    return BeautifulSoup(requests.get(url).text, 'html.parser')

def grab_attr(html, class_name, attr_name): # returns the attribute specified from the class name specified
    soup = new_soup(html)
    return soup.find("div", {"class":class_name})[attr_name]

def scroll_to_bottom(): # Scrolls to the bottom of the page to load in all javascript elements
    lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    match=False
    while(match==False):
        lastCount = lenOfPage
        time.sleep(pause) # time in seconds to load before next scroll
        lenOfPage = driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        if lastCount==lenOfPage:
            match=True

def check_exists_by_class_name(class_name):
    try:
        driver.find_element_by_class_name(class_name)
    except NoSuchElementException:
        return False
    return True

def check_exists_by_class_attribute(class_name, attribute):
    exists = None
    try:
        exists = driver.find_element_by_class_name(class_name).get_attribute(attribute)
    except NoSuchElementException:
        return False
    except AttributeError:
        return False
    return exists is not None

def grab_video_links(): # adds video links to the vid_links list
    link_elems = driver.find_elements_by_css_selector("a[class*='grid__link']")
    for vid_url in link_elems:
        href = vid_url.get_attribute("href")
        print(href)
        if '/video/' in href or '/gif/' in href:
            if 'ifunny.co' in href:
                vid_links.append(href)
            else:
                vid_links.append('ifunny.co'+href)# file_names.append(grab_data_source(href, 'media_fun'))

def load_images(): # appends cropped images to file_names
    img_elems = driver.find_elements_by_class_name("grid__image")
    for img_url in img_elems:
        if '1x1.gif' not in img_url.get_attribute("src").split("images/",1)[1]:
            file_names.append('https://imageproxy.ifunny.co/crop:x-20/images/'+(img_url.get_attribute("src")).split("images/",1)[1]) # Removes watermark
    if check_exists_by_class_name("v-avatar__image") and check_exists_by_class_attribute("v-avatar__image","src"):
        file_names.append("https://imageproxy.ifunny.co/crop:square/user_photos/"+driver.find_element_by_class_name("v-avatar__image").get_attribute("src").split("/")[-1])
    if check_exists_by_class_name("profile__cover-image") and check_exists_by_class_attribute("profile__cover-image","src"):
        file_names.append(driver.find_element_by_class_name("profile__cover-image").get_attribute("src"))

def append_video_links(): # grabs actual video links from their link reference
    count = 0
    for link in vid_links:
        file_names.append(grab_attr(link, 'media_fun', 'data-source')) # Uses bs4
        count+=1
        print('Appending video link '+str(count)+' out of '+str(len(vid_links)))
        # driver.get(link) # uncomment these to instead use selenium
        # time.sleep(pause)
        # file_names.append(driver.find_element_by_css_selector("div[class*='media_fun']").get_attribute("data-source"))

def print_files(): # Used in testing, if used would print out each file name
    for name in file_names:
        print(name)

def grab_link_for_user(user): # Executes functions to collect download links
    set_variables(user)
    driver.get(user)
    scroll_to_bottom()
    grab_video_links()
    load_images()
    append_video_links()
    create_txt()

def create_txt(): # creates the txt file used for downloading files
    try:
        os.makedirs(subdirectory,  exist_ok=True)
        with open(os.path.join(subdirectory,''+subdirectory+'.txt'), 'w') as filehandle:
            for listitem in file_names:
                filehandle.write('%s\n' % listitem)
    except OSError:
        print('Failed to create directory')
    else:
        print('Created directory')

def download_files(directories):
    for user in directories: # Goes through txt files of file downloads and downloads the missing ones
        subdir = (user if '?s=cl' not in user else user[:-5]).split('/')[-1]
        try:
            with open('./'+subdir+'/'+subdir+'.txt', 'r') as filehandle:
                filecontents = filehandle.readlines()
                for line in filecontents:
                    url = line[:-1]
                    if '.mp4' in url: # Fixes mp4 files to always download correctly
                        url = url.split('.mp4')[0]+'.mp4'
                    if os.path.isfile(os.path.join(subdir, url.split('/')[-1])):
                        print('File already exists') # file exists
                    else: # Creates the file
                        print('Downloading Missing file: '+url+'\nin subdirectory '+subdir)
                        r = requests.get(url, allow_redirects=True)
                        open(os.path.join(subdir, url.split('/')[-1]), 'wb').write(r.content) # creates the image and names it
        except OSError:
            print('Failed to download missing file in subdirectory: '+subdir)
        else:
            print('Missing files downloaded')

list_of_users = [] # Holds all of the Users that will be gone through
if '.txt' in URL:
    try: # Read through the txt file of user pages
        with open(URL, 'r') as f:
            userlist = f.readlines()
            for line in userlist:
                list_of_users.append(line if '\n' not in line else line[:-1])
            print(list_of_users)
    except FileNotFoundError:
        print('File not found')
    else:
        print('Read File Contents Successfully')
else:
    list_of_users.append(URL) # If only a single url is passed as an arguement instead of a txt file listing multiple

if mode==0 or mode==1: # Grab links
    for user in list_of_users:
        grab_link_for_user(user)
    driver.close()

if mode==0 or mode==2: # Download Files
    download_files(list_of_users)