#  scrape-mars.py
#
#    This Python script refactors the code inside the Jupyter notebook
#    mission_to_mars.ipynb as a function called scrape() which returns a
#    dictionary with all the scraped data.
#
#    Created by Gilberto Ramirez (gramirez77@gmail.com) as part of the 12th
#    assignment of the UNC Data Analytics Boot Camp.
#
#    v1: August 11, 2019

from bs4 import BeautifulSoup
from splinter import Browser
import urllib.parse
import requests
import pandas as pd

def scrape():
    
    # This dictionary holds the return value that the scrape() function needs to return.
    retval = {}

    # Section 1: NASA Mars News Scraping
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # URL of the NASA Mars News site to be scraped
    url = 'https://mars.nasa.gov/news/'

    # use splinter to create a browser instance, visit the URL, 
    # store the HTML page content rendered by the browser, and exit
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=True)
    browser.visit(url)
    html = browser.html
    browser.quit()

    # BeautifulSoup is a Python library that allows us to pull data out of HTML and XML files.
    # Below I am using the HTML parser included in Python's standard library to make the soup.
    soup = BeautifulSoup(html, 'html.parser')

    result = soup.find("div", class_="list_text")
    news_date = result.find('div', class_='list_date').get_text()
    news_title = result.find('div', class_='content_title').get_text()
    news_p = result.find('div', class_='article_teaser_body').get_text()
    retval['NASA Mars News'] = {'news_date': news_date, 'news_title': news_title, 'news_p': news_p}

    # Section 2: JPL Mars Space Images - Featured Image Scraping
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # URL of the JPL Feature Space image to be scraped
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'

    # use splinter to create a browser instance, visit the URL, 
    # store the HTML page content rendered by the browser, and exit
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=True)
    browser.visit(url)
    html = browser.html
    browser.quit

    # use BeautifulSoup to get the full size featured image URL.
    # after inspection, it seems URL is in the data-fancibox-href 
    # attribute of the <a> tag that uses the id "full_image".
    soup = BeautifulSoup(html, 'html.parser')
    featured_image_relative_url = soup.find('a', id='full_image')['data-fancybox-href']

    # since URL is relative, we can use the urljoin function from 
    # the urllib.parse library to convert it to absolute
    featured_image_url = urllib.parse.urljoin(url, featured_image_relative_url)
    retval['JPL Mars Space Featured Image'] = {'featured_image_url': featured_image_url}

    # Section 3: Mars Weather Scraping
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    url = 'https://twitter.com/marswxreport?lang=en'

    response = requests.get(url)

    soup = BeautifulSoup(response.text, 'html.parser')

    # get most recent twitter
    latest_twitter = soup.find('li', class_='stream-item').find('p', class_='TweetTextSize')

    # remove the <a> tag from the previous twitter 
    latest_twitter.a.extract()

    # save remaining content into mars_weather variable
    mars_weather = latest_twitter.get_text()
    retval['Mars Weather'] = {'mars_weather': mars_weather}

    # Section 4: Mars Facts Scraping
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    url = 'https://space-facts.com/mars/'

    tables = pd.read_html(url)

    df = tables[1]
    df.columns = ['description', 'value']
    df.set_index('description', inplace=True)

    mars_facts_html_table = df.to_html()
    mars_facts_html_table = mars_facts_html_table.replace('\n', '')

    retval['Mars Facts'] = {'mars_facts_html_table': mars_facts_html_table}

    # Section 5: Mars Hemispheres Scraping
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    # URL of the USGS Astrogeology site to be scraped
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'

    # use splinter to create a browser instance, visit the URL, 
    # and store the HTML page content rendered by the browser
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=True)
    browser.visit(url)
    html = browser.html

    # use BeautifulSoup to get the links to each one of the
    # hemisphere images and store them in a list called hrefs
    hrefs = []
    soup = BeautifulSoup(html, 'html.parser')
    results = soup.find('div', id='product-section').find_all('div', class_='description')
    for result in results:
        hrefs.append(urllib.parse.urljoin(url, result.find('a')['href']))
                    
    # navigate to each Mars hemiphere images, grab the title, and
    # image URL, store in a list of dictionaries structure.
    hemisphere_image_urls = []
    for href in hrefs:
        browser.visit(href)
        html = browser.html
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.find('h2', class_='title').get_text().replace(' Enhanced', '')
        img_url = soup.find('div', class_='downloads').find('a')['href']
        dic = {}
        dic['title'] = title
        dic['img_url'] = img_url
        hemisphere_image_urls.append(dic)

    # close the browser
    browser.quit

    retval['Mars Hemispheres Images'] = hemisphere_image_urls

    return retval
