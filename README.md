# iFunny Meme Scraper
A scraper for the website ifunny.co that will collect the links and download all images and videos posted on a particular user's page

The Scraper requires the use of Selenium because of the javascript loading that takes places on iFunny. The links are then collected after an "infinite scroll" that keeps scrolling to the bottom of the page.
This program was written to support selenium using firefox
If you are new to selenium, don't forget to add the path to the geckodriver.exe to the PATH environment variable

## Optional arguements:
* pause: the length of time between each scroll to the bottom of the page, by default set to 2 seconds
* mode: Mode options are 0 (This is the default) for grab links and download files, 1 for grab links only, and 2 for download only (Requires the previous step to be done first at a seperate time)

- - -

## Installing Dependencies

first install all of the requirements by typing in `pip install ...` where ... is replaced by each requirement (This step can be skipped if you already satisfy the requirements)

List of Requirements: 

* requests
* bs4
* selenium

## Running the Program

Navigate to the python file in cmd, then execute the line `python scraper.py link pause mode` where link is replaced with the iFunny.co user's page such as https://ifunny.co/user/TheLegoManSeries?s=cl

the link can also be replaced with a txt file that has a link on each line of the file, for example:
https://ifunny.co/user/TheLegoManSeries?s=cl
https://ifunny.co/user/WhateverTheUserIsNamed
https://ifunny.co/user/JustKeepAddingMoreUserProfiles

pause is replaced with the amount of time in seconds before the next scroll to bottom, increase this value if your program stops scrolling prematurely

mode is replaced with 0, 1, or 2, as described above under the optional arguements

In the end you could be running any of these example commands:

* `python scraper.py https://ifunny.co/user/TheLegoManSeries?s=cl`

* `python scraper.py https://ifunny.co/user/TheLegoManSeries?s=cl 2`

* `python scraper.py https://ifunny.co/user/TheLegoManSeries?s=cl 2 0`

Or with the txt file being used: 

* `python scraper.py downloadlist.txt`

* `python scraper.py downloadlist.txt 2`

* `python scraper.py downloadlist.txt 2 0`

Make sure to take not of what version of python you are using as the call to python may be py, py3, python, or python3

This also applies to pip, make sure to install depandencies to the correct pip associated with the python environment in use

You can check the version of python by running `python -v` or `python --version` and the same with pip by running `pip --version`
