
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import re
import datetime
import time
import pandas as pd
import os
import json
import logging
import argparse

# import types for type hinting 
from selenium.webdriver.remote.webelement import WebElement



NOW = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
#DATA_PATH = "data"
MAPS_LINK = "https://maps.google.com/"


def get_arguments():
    
    def str2bool(v):
        if isinstance(v, bool):
            return v
        if v.lower() in ('yes', 'true', 't', 'y', '1'):
            return True
        elif v.lower() in ('no', 'false', 'f', 'n', '0'):
            return False
        else:
            raise argparse.ArgumentTypeError('Boolean value expected.')
    # read arguments from the command line
    parser = argparse.ArgumentParser(description="Google Maps Review Scraper")
    parser.add_argument("--driver", type=str, default="./Driver/chromedriver.exe", help="Path to the Chrome driver")
    parser.add_argument("--url", type=str, help="URL of the Google Maps reviews")
    parser.add_argument("--headless", type=str2bool, default=True, help="Run the browser in headless mode, default is True")
    parser.add_argument("--verbose", type=str2bool, default=False, help="Verbose mode, default is False")
    parser.add_argument("--delay", type=int, default=10, help="Delay for the driver, in seconds, default is 10s")
    parser.add_argument("--original", type=str2bool, default=True, help="Get the comment in the original language, default is True")
    parser.add_argument("--language", type=str, default="en", help="Language for the reviews, default is English")  
    parser.add_argument("--concat_extra", type=str2bool, default=False, help="Concatenate extra attributes in a single column, default is False")
    parser.add_argument("--path", type=str, default="data", help="Path to save the data, default is data")
    parser.add_argument("--name", type=str, default="reviews", help="Name of the file to save the data, default is 'reviews'")
    parser.add_argument("--timestamp", type=str2bool, default=True, help="Add timestamp to the file name, default is True")
    parser.add_argument("--log_file", type=str, default=None, help="Name of the log file, default is None, show logs in command line") 
    return parser.parse_args()

class GoogleMapsReviewScraper:
    """
    A class to scrape Google Maps reviews for a given location.
    """
    
    accepted_languages = ["en", "fr", "de", "es", "it", "nl", "ja", "pt", "ru", "zh-CN"]
    
    def __init__(
        self, driver_path, headless=True, verbose=False, delay=10, original=True, language="en", concat_extra=False, log_file=None 
    ):
        # todo: make sure the URL is a valid Google Maps reviews link 
        options = webdriver.ChromeOptions()
        self.reviews = []
        self.now = NOW
        self.headless = headless
        self.original = original
        self.concat_extra = concat_extra
        self.log_file = log_file
        
        # check if the language is accepted
        if language not in self.accepted_languages:
            raise ValueError(f"Language {language} is not accepted.")
        # force language
        #self.url = f"{url}&hl={language}"
        
        level = logging.INFO if verbose else logging.ERROR
        
        if self.log_file:
            logging.basicConfig(filename=f'logs/{log_file}_{NOW}.log', level=level)
        else:
            logging.basicConfig(level=level)
        
        if self.headless:     
            options.add_argument("--headless")
            
        
        # create an instance of the Chrome driver
        self.driver = webdriver.Chrome(executable_path=driver_path,options=options)
        # set the delay for the driver
        self.wait = WebDriverWait(self.driver, delay)
        
        # connect to google maps and accept the cookies   
        try:
            self.driver.get(MAPS_LINK)
        except Exception as e:
            logging.error(f"Error connecting to {MAPS_LINK}")
            raise e
        self.accept_cookies()
        
            
        
    def accept_cookies(self):
        # wait for the page to load and get cookies accept button
        accept_button = self._get_element_("//*[@id='yDmH0d']/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button", type_=By.XPATH)
        accept_button.click()
        logging.info("Cookies accepted")


    def connect(self, url):
      
        try:    
            # connect to the URL and wait for the page to load
            self.driver.get(url)
            # wait for the page to load and get total number of reviews
            total_reviews = self._get_element_('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div/div[2]/div[3]', type_=By.XPATH).text
            total_reviews = int(re.sub(r'\D', '', total_reviews))
            return total_reviews
        except Exception as e:
            logging.error(f"Error connecting to {url}")
            raise e

    def extract_data(self, total_reviews):
        
        # sort reviews by newest
        _= self._get_element_('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[8]/div[2]/button', By.XPATH).click()
        _ = self._get_element_('//*[@id="action-menu"]/div[2]', By.XPATH).click()
        
        # get scroll element
        scrollable_div = self._get_element_('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]', By.XPATH)
        
        current_seen_reviews = 0
        while current_seen_reviews < total_reviews:
            # get new reviews
            reviews = self._get_element_(target='jJc9Ad', type_=By.CLASS_NAME, multiple=True)
            reviews_data = [self._extract_review_(review, concat_extra=self.concat_extra) for review in reviews[current_seen_reviews:]]
            self.reviews.extend(reviews_data)
            current_seen_reviews = len(reviews)
            #logging.info(f"Total reviews extracted: {current_seen_reviews}/{total_reviews}")
            # scroll to load more reviews
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        

    def save_data(self, path= "data", name='', timestamp=True):
        if not os.path.exists(path):
            os.makedirs(path)
            
        if timestamp:
            name = f"{name}_{self.now}"
            
        if self.concat_extra:
            df = pd.DataFrame(self.reviews)
            df.to_csv(f"{path}/{name}.csv", index=False)
        else:
            with open(f"{path}/{name}.json", "w") as f:
                json.dump(self.reviews, f)
        logging.info(f"Data saved to {path}")
        
    def scrap(self, url):
        
            logging.info(f"Scraping {url} ...")
            start = time.time()
            total_reviews = self.connect(url)
            logging.info(f"Connected, Total number of reviews: {total_reviews}")
            if total_reviews == 0:
                logging.warning("No reviews were found, returning None")
                return None
            
            self.extract_data(total_reviews) 
            end = time.time()   
            logging.info(f"Scraping completed in {end-start} seconds") 
            return self.reviews         
        
    def _get_element_(self, target, type_="class", multiple=False):
        """
        Finds and returns a web element based on the given XPath.

        Args:
            driver: The WebDriver instance (e.g., Chrome, Firefox).
            xpath: The XPath string to locate the element.
            timeout: The maximum time to wait for the element (default is 10 seconds).

        Returns:
            WebElement: The located element.

        Raises:
            TimeoutException: If the element is not found within the timeout period.
        """
        
        try:
            if multiple:
                elements = self.wait.until(EC.presence_of_all_elements_located((type_, target)))
            else:
                elements = self.wait.until(EC.presence_of_element_located((type_, target)))
            return elements
        except TimeoutException as e:
            print(f"Error: Unable to locate element with {type} : {target}")
            raise e   
        
    def exit(self, force=False):
        """function to close the browser
        """
        if force:
            self.driver.quit()
            return
        
        if not self.headless:
            _ = input("Press Enter to close the browser")     
        self.driver.quit()
        
    def _extract_review_(self, review_container: WebElement, concat_extra: bool = False) -> dict:
        
        review = {}
        # get username
        review['username'] = review_container.find_element_by_class_name('d4r55').text
        # get rating    
        stars = review_container.find_element_by_class_name('kvMYJc').find_elements_by_class_name('hCCjke')
        review['rating'] = len([star for star in stars if 'elGi1d' in star.get_attribute('class')])
        # get date
        review['date'] = review_container.find_element_by_class_name('rsqaWe').text
        # check if has likes
        try:
            review['likes'] = review_container.find_element_by_class_name('pkWtMe').text
        except NoSuchElementException as _:
            review['likes'] = 0
   

        # get comment text
        try:
            comment_section = review_container.find_element_by_class_name('MyEned')
            #  check if comment can be expanded
            try:
                _ = comment_section.find_element_by_tag_name('button').click()
            except NoSuchElementException as _: # do nothing if the button is not found
                pass
            review['comment'] = comment_section.find_element_by_class_name('wiI7pd').text
        except NoSuchElementException as _:
            review['comment'] = None

        # check for extra attributes
        
        if concat_extra:
            review['extra'] = ''
        try:
            extra = review_container.find_element_by_css_selector("div[jslog='127691']")
            spans = extra.find_elements_by_class_name('RfDO5c')
            for i in range(0, len(spans), 2):
                key = spans[i].text
                value = spans[i+1].text
                if not concat_extra:
                    review[key] = value
                else:
                    review['extra'] = "," + f"{key}:{value}"
        except NoSuchElementException as _: # no extra attributes, do nothing
            pass
        
        if self.original: # get the original comment 
            try:
                _ = review_container.find_element_by_class_name('oqftme').find_element_by_tag_name('button').click()
                review['original']  = comment_section.find_element_by_class_name('wiI7pd').text
            except NoSuchElementException as _: # no translation, original comment is the same as the comment
                review['original'] = review['comment']
                 
        logging.debug(f"add Review: {review}")
        return review
    
    def reset(self):
        self.reviews = []
        self.now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        logging.info("Resetting the scraper")



if __name__ == "__main__":
    
    args = get_arguments()
    scrapper = GoogleMapsReviewScraper(driver_path=args.driver, headless=args.headless, verbose=args.verbose, delay=args.delay, 
                                       original=args.original, language=args.language, concat_extra=args.concat_extra, log_file=args.log_file)
    
    _ = scrapper.scrap(args.url)
    scrapper.save_data(path=args.path, name=args.name, timestamp=args.timestamp)
    scrapper.exit(force=True)
