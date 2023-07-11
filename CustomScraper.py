from selenium import webdriver
import time
from selenium.webdriver.common.keys import Keys
from parsel import Selector
import validators
import requests
from dotenv import load_dotenv
import os
load_dotenv()

class LinkedIn():
    def __init__(self):
        # direct the webdriver to where the browser file is:
        driver_path = os.environ['CHROMEDRIVER_PATH']
        self.driver = webdriver.Chrome(executable_path=driver_path)
        # your secret credentials:
        email = os.environ['LINKEDIN_USERNAME']
        password = os.environ['LINKEDIN_PASSWORD']
        # Go to linkedin and login
        self.driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
        time.sleep(3)
        self.driver.find_element_by_id('username').send_keys(email)
        self.driver.find_element_by_id('password').send_keys(password)
        self.driver.find_element_by_id('password').send_keys(Keys.RETURN)
        time.sleep(4)


    def scrape_url_data(self, url):
        """
        Scrapes data from a given URL and returns a dictionary with the extracted information.
        
        Args:
            url (str): The URL to scrape data from.
        
        Returns:
            dict: A dictionary containing the extracted data, including 'firstname', 'lastname', 'job', 'url', and 'company'.
        """
        # Get the profile URL
        self.driver.get(url)
        
        # Add a 5 second pause when loading each URL
        time.sleep(5)
        
        # Assign the source code for the webpage to the variable 'sel'
        sel = Selector(text=self.driver.page_source)
        
        # Extract the text from the class containing the name
        name = sel.xpath('//h1/text()').extract_first()
        if name:
            name = name.strip()
        
        # Extract the text from the class containing the job title
        job_title = sel.xpath('//div[starts-with(@class, "pv-text-details__left-panel")]/div[starts-with(@class, "text-body-medium")]/text()').extract_first()
        if job_title:
            job_title = job_title.strip()
        
        # Extract the text from the class containing the company
        company = sel.xpath('//h2/div/text()').extract_first()
        if company:
            company = company.strip()

        # Process the name
        namelist = name.split(' ')
        firstname = namelist[0]
        if len(namelist) > 1:
            lastname = namelist[1]
        else:
            lastname = ''
        
        return {'firstname': firstname, 'lastname': lastname, 'job': job_title, 'url': url, 'company': company}

    def close_driver(self):
        self.driver.quit()


# Scraper for google search linked URLS
class URLScrapper():
    def __init__(self):
        # direct the webdriver to where the browser file is:
        self.driver_path = os.environ['CHROMEDRIVER_PATH']
        self.driver = webdriver.Chrome(executable_path=self.driver_path)
        self.urls = []

    def get_urls_for_company(self, company, pages=1):
        """
        Get LinkedIn URLs for a given company.
        
        Args:
            company (str): The company name to search for.
            pages (int): The number of search result pages to scrape.
        
        Returns:
            None
        """
        # Go to Google
        self.driver.get('https://www.google.ca')
        time.sleep(3)
        
        # Locate search form by name
        search_query = self.driver.find_element_by_name('q')
        
        # Simulate the search text key strokes
        search_query.send_keys('site:linkedin.com/in/ AND ("talent acquisition" OR "recruiter") AND "canada" AND "'+company+'"')
        
        # Simulate the return key
        search_query.send_keys(Keys.RETURN)
        time.sleep(1)
        
        # Loop n times for each page
        for i in range(pages):
            # Locate URL by class name
            linkedin_urls = self.driver.find_elements_by_xpath('//div[@class="yuRUbf"]/a') # MAY CAUSE ERRORS
            
            # Print all elements within the list
            for a in linkedin_urls:
                url = a.get_attribute('href')
                if validators.url(url) == True:
                    self.urls.append(url)
            
            # Go to next page
            self.driver.find_element_by_link_text('Next').click()
            time.sleep(2)

    def print_urls(self):
        """
        Prints the URLs in the list.

        Args:
            self: The instance of the class.

        Returns:
            None
        """
        for h in self.urls:
            # Print each URL
            print(h)

    def add_urls_to_database(self):
        """
        Add URLs to the database.

        This function takes a list of URLs and adds them to the database using the LinkedInURLs model.
        If a URL already exists in the database, it will be skipped.

        Args:
            self (obj): The current instance of the class.

        Returns:
            None
        """
        from sqlite3 import IntegrityError  # Import the IntegrityError exception from sqlite3 module
        from Models import db, LinkedInURLs  # Import db and LinkedInURLs models from the Models module
        import sys  # Import sys module

        for url in self.urls:  # Iterate over each URL in the list of URLs
            try:
                db.session.add(LinkedInURLs(linkedinURL=url))  # Create a new LinkedInURLs object with the current URL and add it to the session
                db.session.commit()  # Commit the changes to the database
                print('added url ' + str(url))  # Print a success message
            except IntegrityError:  # Handle IntegrityError exception
                print('--------------- ERROR AT url ' + str(url) + ' Reason: Data already exists')
                db.session.rollback()  # Rollback the session to undo the changes
            except:  # Handle any other exception
                print('--------------- ERROR AT url ' + str(url) + ' Reason: ' + str(sys.exc_info()[0]))
                db.session.rollback()  # Rollback the session to undo the changes
    
    def empty_url_list(self):
        self.urls = []

    def close_driver(self):
        self.driver.quit()

class EmailFinder():
    def __init__(self,auth_key):
        self.base_url = "https://api.skrapp.io/api/v2/"
        self.access_key = auth_key
        self.headers = { 'X-Access-Key': self.access_key, 'Content-Type': 'application/json'}
        self.payload={}
    
    def find_email(self,fname,lname,domain):
        url = self.base_url+'find?firstName='+fname+'&lastName='+lname+'&domain='+domain
        response = requests.request("GET", url, headers=self.headers, data=self.payload)
        if '200' in str(response):
            response = response.json()
            try:
                return {'email':response['email'], 'accuracy':response['accuracy']}
            except:
                return 'error'
        else:
            if self.get_remaining_balance() == 0:
                print('BALANCE REMAINING: '+str(self.get_remaining_balance()))
                exit()
            return 'error'
    
    def get_remaining_balance(self):
        url = self.base_url+'account'
        response = requests.request("GET", url, headers=self.headers, data=self.payload)
        response = response.json()
        return response["credit"]["email"]["quota"]-response["credit"]["email"]["used"]