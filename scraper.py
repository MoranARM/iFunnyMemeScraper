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
pause = 2 if len(argv)<3 else int(argv[2]) # increase if page does not load images fast enough
mode = 0 if len(argv)<4 else int(argv[3]) # sets default mode to 0
URL = ""+site
subdirectory = (URL if '?s=cl' not in URL else URL[:-5]).split('/')[-1]
print(subdirectory)
driver = webdriver.Firefox() # Requires selenium webdriver
file_names = []  # a list to store the names that will be used to grab each image

def set_variables(url): # Resets the gloabl variables used for each user
    global URL, subdirectory, file_names, vid_links # Allows the function to reset global variables
    URL = ''+url if 'http' in url else 'https://'+url
    subdirectory = (URL if '?s=cl' not in URL else URL[:-5]).split('/')[-1]
    file_names = []

def new_soup(url):  # function to create new html objects from bs
    return BeautifulSoup(requests.get(url).text, 'html.parser')

def grab_attr(html, class_name, attr_name): # returns the attribute specified from the class name specified
    soup = new_soup(html)
    div_found = soup.find("div", {"class":class_name})
    if div_found!=None:
        return div_found[attr_name]

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

def grab_video_links(): # adds video links to the file_names list (formerly added to Deprecated: vid_links) 
    vid_class = '_2bHN' # was formerly grid__link
    link_elems = driver.find_elements_by_css_selector("video[class*="+vid_class+"]")# video tag was formerly an 'a' tag
    for vid_url in link_elems:
        src = vid_url.get_attribute("data-src")# Attribute of url now stored in src rather than href
        if (src==None): # If unable to locate link, look in a child element
            src = vid_url.find_element_by_xpath("//source[@type='video/mp4']").get_attribute("src")
        print(src) # Display the video link found
        if '/video/' in src or '/videos/' in src or '/gif/' in src:
            if 'ifunny.co' in src:
                file_names.append(src)#vid_links deprecated, now directly added to file_names
            else:
                file_names.append('ifunny.co'+src)# file_names.append(grab_data_source(href, 'media_fun'))

def load_images(): # appends cropped images to file_names
    img_class = '_17ZL' # was formerly grid__image
    avatar_class = '_30tR' # was formerly v-avatar__image
    banner_class = '_3oof' # was formerly profile__cover-image
    img_elems = driver.find_elements_by_css_selector("img[class*="+img_class+"]")
    for img_url in img_elems:
        if 'images/' in img_url.get_attribute("src"):
            img_name = img_url.get_attribute("src").split("images/",1)[1]
            if '1x1' not in img_name or '.gif' not in img_name:
                file_names.append('https://imageproxy.ifunny.co/crop:x-20/images/'+(img_name)) # Removes watermark
    if check_exists_by_class_name(avatar_class) and check_exists_by_class_attribute(avatar_class,'src'):
        file_names.append('https://imageproxy.ifunny.co/crop:square/user_photos/'+driver.find_element_by_class_name(avatar_class).get_attribute('src').split('/')[-1])
    if check_exists_by_class_name(banner_class) and check_exists_by_class_attribute(banner_class,'src'):
        file_names.append(driver.find_element_by_class_name(banner_class).get_attribute('src'))

def print_files(): # Used in testing, if used would print out each file name
    for name in file_names:
        print(name)

def grab_link_for_user(user): # Executes functions to collect download links
    set_variables(user)
    driver.get(URL)
    scroll_to_bottom()
    grab_video_links()
    load_images()
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
        if (user!=None) and ('.' in user):
            grab_link_for_user(user)
    driver.close()

if mode==0 or mode==2: # Download Files
    print('Downloading Files')
    download_files(list_of_users)