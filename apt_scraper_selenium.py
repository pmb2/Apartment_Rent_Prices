# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 13:39:55 2020

@author: bdaet
"""
import seleniumwire.webdriver
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import re

# initializing the webdriver
options = seleniumwire.webdriver.ChromeOptions()

# set path to driver
driver = seleniumwire.webdriver.Chrome(options=options)
driver.set_window_size(1120, 1000)
place = 'schenectady-ny'
url = f'https://www.apartments.com/{place}/'

# number of pages to scrape, looks like there are 25 listings per page
num_pages = 28

# max delay for WebDriverWait function
max_delay = 12

df = pd.DataFrame()


def main():
    # looping through specified number of pages
    for j in range(num_pages):
        print('Page Number: {}'.format('' + str(j + 1)))

        if j > 0:
            driver.get(url + '/' + str(j + 1) + '/')
        else:
            driver.get(url)

        # wait for web page to load before getting list of placardTitle elements
        WebDriverWait(driver, max_delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'placard-content')))

        # going through each apartment listing on page
        num_placards = len(driver.find_elements(By.CLASS_NAME, 'placard-content'))
        for i in range(num_placards):
            if i % 2 == 0:
                print('\nProgess: {}\n\n'.format('' + str(i + 1) + '/' + str(num_placards)))

            # wait for web page to load before getting list of placardTitle elements
            WebDriverWait(driver, max_delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'placard-content')))
            apt_buttons = driver.find_elements(By.CLASS_NAME, 'property-link')
            try:
                apt_buttons[i].click()
            except ElementNotInteractableException:
                i += 1
                continue
            # wait for web page to load before scraping
            try:
                WebDriverWait(driver, max_delay).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'pricingGridTitleBlock')))
            except TimeoutException:
                driver.execute_script("window.stop();")
                print("Timeout exception caught, continuing...")

            # getting elements for entire property
            titles = driver.find_elements(By.CLASS_NAME, 'propertyName')
            addresses = driver.find_elements(By.CLASS_NAME, 'delivery-address')
            listings_dict = {}
            # get model information
            try:
                model_names = driver.find_elements(By.CLASS_NAME, 'modelName')
                for model_name in model_names:
                    print(f'Model Name: {model_name.text}')
                    listings_dict['Model Name'].append(model_name.text)
                rent_labels = driver.find_elements(By.CLASS_NAME, 'rentLabel')
                for rent in rent_labels:
                    print(f'Rent: {rent.text}')
                    listings_dict['Rent'].append(rent.text)
                detailsTextWrapper = driver.find_elements(By.CLASS_NAME, 'detailsTextWrapper')
                for detail in detailsTextWrapper:
                    print(f'Details: {detail.text}')
                    listings_dict['Details'].append(detail.text)
            except NoSuchElementException:
                pass
            except KeyError:
                pass
            # get property information
            for title, address in zip(titles, addresses):
                print(f'{title.text}')
                print(f'Address: {address.text}')
                if title.text not in listings_dict:
                    listings_dict[title.text] = []
                listings_dict[title.text].append(address.text)

            amenity_rows = driver.find_elements(By.CLASS_NAME, 'specInfo')
            amenity_data = []
            print('Amenities: ')
            for row in amenity_rows:
                amenity_data.append(row.text)
            amenity_string = ', '.join(amenity_data)
            print(amenity_string)
            try:
                listings_dict['Amenities'].append(amenity_string)
            except KeyError:
                listings_dict['Amenities'] = [amenity_string]

            # getting elements for each apartment
            labels, details = driver.find_elements(By.CLASS_NAME, 'rentInfoLabel'), driver.find_elements(By.CLASS_NAME,
                                                                                                         'rentInfoDetail')
            for label, detail in zip(labels, details):
                print(f'{label.text}: {detail.text}')
                if label.text not in listings_dict:
                    listings_dict[label.text] = []
                listings_dict[label.text].append(detail.text)

            listing_df = pd.DataFrame(listings_dict)

            # adding data from this listing to larger dataframe with data for all listings
            df = pd.concat([df, listing_df], axis=0, sort=False)

            # resetting index for dataframe
            df.reset_index(drop=True, inplace=True)
            # create string dt to store current date and time
            dt = pd.to_datetime('today').strftime('%Y-%m-%d_%H-%M-%S')
            df.to_csv(f'apt_data\\{place.replace("-", "_")}{dt}.csv', index=False)

            driver.back()  # to go back to main page
