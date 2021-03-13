from selenium.webdriver  import Chrome
import pytest
#driver.get('http://www.thetestingworld.com/testings')

@pytest.fixture(scope="module")
def set_path():
    global driver
    path = "/Users/spyrosdragazis/Downloads/chromedriver"
    driver = Chrome(executable_path=path)
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
