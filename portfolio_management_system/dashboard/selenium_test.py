import unittest
import time
import json
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import requests

chromeOptions = Options()
chromeOptions.headless = True

# Login Test
class Login(unittest.TestCase):
        
    def setUp(self):
        self.driver = webdriver.Chrome('/usr/local/bin/chromedriver')

    def test_login(self):
        driver = self.driver
        driver.get("http://127.0.0.1:8000/accounts/login/")

        login = driver.find_element(By.ID, "id_login")
        login.send_keys("vansh.jain")
        password = driver.find_element(By.ID, "id_password")
        password.send_keys("vansh.jain")
        loginBtn = driver.find_element(By.CLASS_NAME, "btn")
        loginBtn.click()

        
        assert "http://127.0.0.1:8000/" == driver.current_url

    def tearDown(self):
        self.driver.close()

# Dashboard Test
class Dashboard(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome('/usr/local/bin/chromedriver')

    def test_dashboard(self):
        driver = self.driver
        driver.get("http://127.0.0.1:8000/accounts/login/")

        login = driver.find_element(By.ID, "id_login")
        login.send_keys("vansh.jain")
        password = driver.find_element(By.ID, "id_password")
        password.send_keys("vansh.jain")
        loginBtn = driver.find_element(By.CLASS_NAME, "btn")
        loginBtn.click()


        # dashboardBtn = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]/header/div/div/nav/div/div/ul/li[3]")
        # dashboardBtn.click()
        driver.get("http://127.0.0.1:8000/dashboard")

        if driver.current_url != 'http://127.0.0.1:8000/dashboard':
            assert False
        elif driver.current_url == 'http://127.0.0.1:8000/dashboard':
            assert True

    def tearDown(self):
        self.driver.close()

# Add Stock Holding Test
class Portfolio(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome('/usr/local/bin/chromedriver')

    def test_portfolio(self):
        driver = self.driver

        driver.get("http://127.0.0.1:8000/accounts/login/")

        login = driver.find_element(By.ID, "id_login")
        login.send_keys("vansh.jain")
        password = driver.find_element(By.ID, "id_password")
        password.send_keys("vansh.jain")
        loginBtn = driver.find_element(By.CLASS_NAME, "btn")
        loginBtn.click()

        driver.get("http://127.0.0.1:8000/dashboard")

        addStockHolding = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div/div[4]/div/div/div/h4/button')
        addStockHolding.click()


        print(addStockHolding)

        WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, "company")))

        stockTicker = Select(driver.find_element(By.ID, 'company'))
        stockTicker.select_by_index(0)

        # WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID, "example-date-input")))
        date_element = driver.find_element(By.ID, 'example-date-input')
        print(date_element.get_attribute('value'))


        portfolioNum = Select(driver.find_element(By.ID, 'portfolio_select'))
        portfolioNum.select_by_visible_text('portfolio1')

        stocks = driver.find_element(By.ID, 'number-stocks')
        # stocks.send_keys('')
        print(stocks.get_attribute('value'))

        time.sleep(5)
        submitBtn = driver.find_element(By.XPATH, '/html/body/div[1]/div/div/div/div/div[4]/div/div/div/div[1]/div/div/div[2]/form/div[5]/button')
        submitBtn.click()

        WebDriverWait(driver, 60).until(EC.alert_is_present(),'Stock Holding successfully added to your portfolio')

        alert = driver.switch_to.alert
        alert.accept()
        print("alert accepted")

    
    def tearDown(self):
        self.driver.close()

class CheckRealtime(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Chrome('/usr/local/bin/chromedriver')

    def test_realtime(self):
# https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=1min
# https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL&interval=1min&apikey=N8UW6MVBRDUBK0ZV
        url = 'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol=AAPL'
        r = requests.get(url)
        data = r.json()

        try:
            if data["Error Message"] == None:
                assert True    
        except Exception as e:
            print(e)
            if data["Error Message"] != None:
                assert False  
        
    
    def tearDown(self):
        self.driver.close()

if __name__ == "__main__":
    unittest.main()