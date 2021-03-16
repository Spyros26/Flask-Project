import pytest
#driver.get('http://www.thetestingworld.com/testings')
from selenium import webdriver
from selenium.webdriver import Chrome

options = webdriver.ChromeOptions()
options.add_argument('--ignore-ssl-errors=yes')
options.add_argument('--ignore-certificate-errors')
#driver = webdriver.Chrome(options=options)

@pytest.fixture(scope="module")
def set_path():
    global driver
    #Place the path for the driver for your own machine below
    path = "C:\\Users\\User\\Desktop\\chromedriver.exe"
    driver = Chrome(executable_path=path, options=options)
    yield
    driver.close()

def test_registration_valid_data(set_path):
    driver.get('http://localhost:8765/evcharge/api/Login?next=%2Fevcharge%2Fapi%2F')
    driver.maximize_window()
    assert "Login" == driver.title

def test_registration_invalid_data(set_path):
    driver.get('http://localhost:8765/evcharge/api/Login?next=%2Fevcharge%2Fapi%2F')
    driver.maximize_window()
    assert driver.current_url == "http://localhost:8765/evcharge/api/Login?next=%2Fevcharge%2Fapi%2F"

def test_valid_data(set_path):
    driver.get('http://localhost:8765/evcharge/api/Login?next=%2Fevcharge%2Fapi%2F')
    driver.maximize_window()
