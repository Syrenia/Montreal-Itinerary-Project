#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 11 14:42:16 2021

@author: syrenia
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy

attractions = pd.read_csv("/Users/syrenia/Downloads/attractions.csv")
price_maxtrix_uberx = []
price_maxtrix_uberxl = []

vehicle_type = re.compile(r'<span class="iy">(.*)</span><svg class="iz"')
vehicle_price = re.compile(r'<p class="fd cm cn j2 j3">CA(.*)</p>')
#vehicle_space = re.compile(r'<span class="g9">(.*)</span><div class="dl h8 g7 g8 gb">')

    
vehicle_type = re.compile(r'<span class="jd">(.*)</span><svg class="je"')
vehicle_price = re.compile(r'<p class="fd cm cn jh ji">CA(.*)</p>')
#vehicle_space = re.compile(r'<span class="g9">(.*)</span><div class="dl h8 g7 g8 gb">')

vehicle_type = re.compile(r'<span class="j1">(.*)</span><svg class="j2"')
vehicle_price = re.compile(r'<p class="fd cm cn j5 j6">CA(.*)</p>')
    
vehicle_type = re.compile(r'<span class="ip">(.*)</span><svg class="iq"')
vehicle_price = re.compile(r'<p class="fg cm cn iu iv">CA(.*)</p>')
    
vehicle_type = re.compile(r'<span class="ix">(.*)</span><svg class="iy"')
vehicle_price = re.compile(r'<p class="fd cm cn j1 j2">CA(.*)</p>')
    
vehicle_type = re.compile(r'<span class="j5">(.*)</span><svg class="j6"')
vehicle_price = re.compile(r'<p class="fd cm cn j9 ja">CA(.*)</p>')



def login():
    time.sleep(2)
    mobile = chrome.find_element_by_css_selector("input#mobile")
    mobile.send_keys("5143773688")
    mobile.send_keys(Keys.RETURN)
    time.sleep(2)
    
def sms(n):
    sms = chrome.find_element_by_css_selector("input#smsOTP")
    sms.send_keys(n)
    time.sleep(2)
    sms.send_keys(Keys.RETURN)
    password = chrome.find_element_by_css_selector("input#password")
    password.send_keys("19971114wthxxd")
    time.sleep(2)
    password.send_keys(Keys.RETURN)

chrome= webdriver.Chrome("/Users/syrenia/Downloads/chromedriver")
chrome.get("https://m.uber.com/looking?uclick_id=669e7b22-a3fe-44cc-a6fd-3ad1b406843a")
login()
sms("2520")

def clickdetail():
    detail = chrome.find_element_by_xpath("/html/body/div/div[2]/div[2]/div[1]/div[3]/div[4]/div[1]")
    detail.click()

def prepare():
    location = chrome.find_element_by_css_selector("input")
    Action = ActionChains(chrome)
    Action.send_keys_to_element(location, "3575 University Street, Montreal, QC").perform()
    time.sleep(2)
    clickdetail()
    time.sleep(2)
    Action.send_keys_to_element(location, "McGill University").perform()
    time.sleep(2)
    clickdetail()

def read_attractions(n):
    return attractions['address'].iloc[n]

def get_info():
    for i in range(30):
        data_uberx = [0]*30
        data_uberxl = [0]*30
        #pickup = chrome.find_element_by_xpath("//*[@id='booking-experience-container']/div/div[2]/div/div[2]/div[1]/div[2]")
        pickup = chrome.find_element_by_xpath('//*[@id="booking-experience-container"]/div/div[2]/div/div/div[1]/div[2]')
        pickup.click()
        #Action.send_keys_to_element(pickup, read_attractions(i)).perform()
        location = chrome.find_element_by_css_selector("input")
        location.send_keys(read_attractions(i))
        time.sleep(5)
        clickdetail()
        time.sleep(2)
        for j in range(30):
            if i==j:
                continue
            else:
                #drop = chrome.find_element_by_xpath("//*[@id='booking-experience-container']/div/div[2]/div/div[2]/div[2]/div[2]")
                drop = chrome.find_element_by_xpath('//*[@id="booking-experience-container"]/div/div[2]/div/div/div[2]/div[2]')
                drop.click()
                location = chrome.find_element_by_css_selector("input")
                location.send_keys(read_attractions(j))
                #Action.send_keys_to_element(drop, read_attractions(j)).perform()
                time.sleep(4)
                clickdetail()
                time.sleep(7)
                html = chrome.page_source
                soup = BeautifulSoup(html,"html.parser")
                vehicle = soup.select('div[data-test="vehicle-view-container"]')
                for item in vehicle:
                    item = str(item)
                    type_ = re.findall(vehicle_type, item)[0]
                    #space = re.findall(vehicle_space, item)[0]
                    price = re.findall(vehicle_price, item)[0]
                    if type_== 'UberX':
                        data_uberx[j] = price
                    if type_== 'UberXL':
                        data_uberxl[j] = price
            time.sleep(2)
        price_maxtrix_uberx.append(data_uberx)
        price_maxtrix_uberxl.append(data_uberxl)
        time.sleep(5)


def test_re():
    html = chrome.page_source
    soup = BeautifulSoup(html,"html.parser")
    vehicle = soup.select('div[data-test="vehicle-view-container"]')
    print(vehicle)


def save():
    matrix1 = numpy.array(price_maxtrix_uberx)
    matrix2 = numpy.array(price_maxtrix_uberxl)
    df1 = pd.DataFrame(matrix1, columns=list(range(30)))
    df2 = pd.DataFrame(matrix2, columns=list(range(30)))
    df1.to_csv("/Users/syrenia/Downloads/price_matrix_uberx12+.csv")
    df2.to_csv("/Users/syrenia/Downloads/price_matrix_uberxl12+.csv")

def scrap(n):
    html = chrome.page_source
    soup = BeautifulSoup(html,"html.parser")
    vehicle = soup.select('div[data-test="vehicle-view-container"]')
    for item in vehicle:
        item = str(item)
        type_ = re.findall(vehicle_type, item)[0]
        #space = re.findall(vehicle_space, item)[0]
        price = re.findall(vehicle_price, item)[0]
        if type_== 'UberX':
            data_uberx[n] = price
        if type_== 'UberXL':
            data_uberxl[n] = price


def complement():
    for i in range(14,30):
        #pickup = chrome.find_element_by_xpath("//*[@id='booking-experience-container']/div/div[2]/div/div[2]/div[1]/div[2]")
        pickup = chrome.find_element_by_xpath('//*[@id="booking-experience-container"]/div/div[2]/div/div/div[1]/div[2]')
        pickup.click()
        #Action.send_keys_to_element(pickup, read_attractions(i)).perform()
        location = chrome.find_element_by_css_selector("input")
        location.send_keys(read_attractions(i))
        time.sleep(5)
        clickdetail()
        time.sleep(2)
        for j in range(i):
            #drop = chrome.find_element_by_xpath("//*[@id='booking-experience-container']/div/div[2]/div/div[2]/div[2]/div[2]")
            drop = chrome.find_element_by_xpath('//*[@id="booking-experience-container"]/div/div[2]/div/div/div[2]/div[2]')
            drop.click()
            location = chrome.find_element_by_css_selector("input")
            location.send_keys(read_attractions(j))
            #Action.send_keys_to_element(drop, read_attractions(j)).perform()
            time.sleep(4)
            clickdetail()
            time.sleep(7)
            html = chrome.page_source
            soup = BeautifulSoup(html,"html.parser")
            vehicle = soup.select('div[data-test="vehicle-view-container"]')
            for item in vehicle:
                item = str(item)
                type_ = re.findall(vehicle_type, item)[0]
                #space = re.findall(vehicle_space, item)[0]
                price = re.findall(vehicle_price, item)[0]
                if type_== 'UberX':
                    price_maxtrix_uberx[i-12][j] = price
                if type_== 'UberXL':
                    price_maxtrix_uberxl[i-12][j] = price
            time.sleep(2)
        time.sleep(5)



        
