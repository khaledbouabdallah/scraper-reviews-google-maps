from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re
import datetime
import time
import pandas as pd
import os
import json
import logging
# import types for type hinting 
from selenium.webdriver.remote.webelement import WebElement




class GoogleMapsReviewScraper:
    """
    A class to scrape Google Maps reviews for a given location.
    """
    
    accepted_languages = ["en", "fr", "de", "es", "it", "nl", "ja", "pt", "ru", "zh-CN"]
    
    def __init__(
        self, url, driver_path, headless=True, verbose=False, delay=10, original=True, language="en", concat_extra=False
    ):
        # todo: make sure the URL is a valid Google Maps link google.*/maps/place/*
        self.url = url
        options = webdriver.ChromeOptions()
        self.reviews = []
        self.now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.headless = headless
        self.original = original
        self.concat_extra = concat_extra
        
        # check if the language is accepted
        if language not in self.accepted_languages:
            raise ValueError(f"Language {language} is not accepted.")
        # force language
        self.url = f"{self.url}&hl={language}"
        #options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
        
        if verbose:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.ERROR)
        
        if self.headless:     
            options.add_argument("--headless")
            

            
        # create an instance of the Chrome driver
        self.driver = webdriver.Chrome(executable_path=driver_path,options=options)
        # set the delay for the driver
        self.wait = WebDriverWait(self.driver, delay)
        

    def connect(self):
        
        try:    
            # connect to the URL and wait for the page to load
            self.driver.get(self.url)
            # wait for the page to load and get accept button
            try:
                accept_button = self._get_element_("//*[@id='yDmH0d']/c-wiz/div/div/div/div[2]/div[1]/div[3]/div[1]/div[1]/form[2]/div/div/button", type_=By.XPATH)
                accept_button.click()
                logging.info("Button accepted")
            except:
                pass
            # wait for the page to load and get total number of reviews
            total_reviews = self._get_element_('//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div/div[2]/div[3]', type_=By.XPATH).text
            total_reviews = int(re.sub(r'\D', '', total_reviews))
            return total_reviews
        except Exception as e:
            logging.error(f"Error connecting to {self.url}")
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
            logging.info(f"Total reviews extracted: {current_seen_reviews}/{total_reviews}")
            # scroll to load more reviews
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_div)
        

    def save_data(self, path= "data"):
        if not os.path.exists(path):
            os.makedirs(path)
            
        if self.concat_extra:
            df = pd.DataFrame(self.reviews)
            df.to_csv(f"{path}/reviews_{self.now}.csv", index=False)
        else:
            with open(f"{path}/reviews_{self.now}.json", "w") as f:
                json.dump(self.reviews, f)
        logging.info(f"Data saved to {path}")
    def run(self):
        
        try:
            start = time.time()
            logging.info("Starting the scraping process")
            total_reviews = self.connect()
            logging.info(f"Connected, Total number of reviews: {total_reviews}")
            if total_reviews == 0:
                logging.warning("No reviews found, exiting the process")
                self.exit()
            self.extract_data(total_reviews)
            end = time.time()   
            logging.info(f"Scraping completed in {end-start} seconds")          
            self.save_data()
 
        except Exception as e:
                logging.error(f"Error: {e}")
        finally:
             self.exit()
        
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
        except Exception as e:
            print(f"Error: Unable to locate element with {type} : {target}")
            raise e   
        
    def exit(self):
        if not self.headless:
            _ = input("Press Enter to close the browser")     
        self.driver.quit()
        
    def _extract_review_(self, review_container: WebElement, concat_extra: bool = False) -> dict:
        
        review = {}
        print("======================================")
        # get username
        review['username'] = review_container.find_element_by_class_name('d4r55').text
        # get rating    
        stars = review_container.find_element_by_class_name('kvMYJc').find_elements_by_class_name('hCCjke')
        review['rating'] = len([star for star in stars if star.value_of_css_property('color') == 'rgba(255, 187, 41, 1)'])
        # get date
        review['date'] = review_container.find_element_by_class_name('rsqaWe').text
        # check if has likes
        try:
            review['likes'] = review_container.find_element_by_class_name('pkWtMe').text
        except:
            review['likes'] = 0
   

        # get comment text
        try:
            comment_section = review_container.find_element_by_class_name('MyEned')
            #  check if comment can be expanded
            try:
                _ = comment_section.find_element_by_tag_name('button').click()
            except:
                pass
            review['comment'] = comment_section.find_element_by_class_name('wiI7pd').text
        except:
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
        except:
            pass
        
        if self.original:
            try:
                _ = review_container.find_element_by_class_name('oqftme').find_element_by_tag_name('button').click()
                print("got original")
                review['original']  = comment_section.find_element_by_class_name('wiI7pd').text
            except:
                review['original'] = review['comment']
                
            
        logging.info(f"add Review: {review}")
        return review


if __name__ == "__main__":
    URL = "https://www.google.com/maps/place/Wild+Code+School/@48.868858,2.4034931,17z/data=!3m1!5s0x47e66d9bebbd073f:0xe59d9cab917bdad8!4m8!3m7!1s0x47e671e4f9ed9097:0x21f0557e9b283397!8m2!3d48.8688545!4d2.406068!9m1!1b1!16s%2Fg%2F11fy11pqtq?entry=ttu&g_ep=EgoyMDI0MTIxMS4wIKXMDSoASAFQAw%3D%3D"
    #URL = 'https://www.google.com/maps/place/ISKCON+temple+Bangalore/@13.0098328,77.5510964,15z/data=!4m7!3m6!1s0x0:0x7a7fb24a41a6b2b3!8m2!3d13.0098328!4d77.5510964!9m1!1b1'
    DriverLocation = "./Driver/chromedriver.exe"
    scrapper = GoogleMapsReviewScraper(url=URL, driver_path=DriverLocation, headless=False, verbose=True, delay=5, original=True, language="en", concat_extra=True)
    scrapper.run()