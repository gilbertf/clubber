#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
import unittest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import sys

def gotoElement(driver, e):
    #Most likely "scroll-behavior: smooth" makes us miss the button to click on
    driver.execute_script("arguments[0].scrollIntoView();", e);
    import time
    time.sleep(1)

def saveScreen(self, name):
    import os
    p = "screenshots/" + self.language + "/" + unittest.TestCase.id(self).split(".")[2]
    if not os.path.exists(p):
        os.makedirs(p)
    self.driver.save_screenshot(p + "/" + name + ".png")

def register(self, usr, pwd, email, language):
    saveScreen(self, "home")

    reg = self.driver.find_element(By.ID, "btn_register")
    reg.click()
    saveScreen(self, "register_empty")

    self.driver.find_element(By.ID, "id_username").send_keys(usr)
    self.driver.find_element(By.ID, "id_password1").send_keys(pwd)
    self.driver.find_element(By.ID, "id_password2").send_keys(pwd)
    self.driver.find_element(By.ID, "id_email").send_keys(email)
    self.driver.find_element(By.ID, "id_language").send_keys(language)

    saveScreen(self, "register_full")

    btn = self.driver.find_element(by = By.CSS_SELECTOR, value=".btn")
    gotoElement(self.driver, btn)
    btn.click()
    saveScreen(self, "register_redirect")

def logout(self):
    self.driver.find_element(By.ID, "btn_settings").click()
    saveScreen(self, "logout_pre")
    self.driver.find_element(By.ID, "btn_logout").click()
    saveScreen(self, "logout_post")

def login(self, usr, pwd):
    self.driver.find_element(By.ID, "btn_login").click()
    saveScreen(self, "login_empty")
    self.driver.find_element(By.ID, "id_username").send_keys(usr)
    self.driver.find_element(By.ID, "id_password").send_keys(pwd)
    saveScreen(self, "login_full")
    self.driver.find_element(by = By.CSS_SELECTOR, value=".btn").click()
    saveScreen(self, "login_redirect")

def makeAdmin(usr):
    from django.contrib.auth import get_user_model
    import os, django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "clubber.settings")
    django.setup()
    u = get_user_model()
    u = u.objects.filter(username=usr).get()
    u.is_superuser = True
    u.is_staff = True
    u.save()

def runServer():
    import os
    os.remove("db.sqlite3")
    #os.system("python3 manage.py collectstatic")
    os.system("python3 manage.py makemigrations events")
    os.system("python3 manage.py migrate")
    import subprocess
    sp = subprocess.Popen(["python3","manage.py","runserver"])
    import time
    time.sleep(3)
    return sp

def newType(self, typ):
    self.driver.find_element(By.ID, "btn_settings").click()
    self.driver.find_element(By.ID, "btn_event_types").click()
    self.driver.find_element(By.ID,"btn_typ_add").click()
    self.driver.find_element(By.ID, "id_name").send_keys(typ)
    saveScreen(self, "new_type_full")
    self.driver.find_element(By.ID,"btn_typ_add_confirm").click()
    saveScreen(self, "new_type_redirect")

def newEvent(self, start_time, end_time):
    self.driver.find_element(By.ID, "btn_event_add").click()
    saveScreen(self, "newEvent_empty")
    st = self.driver.find_element(By.ID,"id_start_time")
    self.driver.execute_script ("arguments[0].value='" + start_time + ":00';", st)
    et = self.driver.find_element(By.ID,"id_end_time")
    self.driver.execute_script ("arguments[0].value='" + end_time + ":00';", et)
    btn = self.driver.find_element(By.ID,"btn_event_add_confirm")
    gotoElement(self.driver, btn)
    btn.click()
    saveScreen(self, "newEvent_redirect")

def modifyEvent(self, start_time, end_time):
    self.driver.find_element(By.ID, "btn_event_modify").click()
    saveScreen(self, "modifyEvent_open")
    st = self.driver.find_element(By.ID,"id_start_time")
    self.driver.execute_script ("arguments[0].value='" + start_time + ":00';", st)
    et = self.driver.find_element(By.ID,"id_end_time")
    self.driver.execute_script ("arguments[0].value='" + end_time + ":00';", et)
    saveScreen(self, "modifyEvent_changed")
    btn = self.driver.find_element(By.ID,"btn_event_modify_confirm")
    gotoElement(self.driver, btn)
    btn.click()
    saveScreen(self, "modifyEvent_redirect")

def participateEvent(self):
    saveScreen(self, "participateEvent_0")
    self.driver.find_element(By.ID, "btn_event_participate_set").click()
    saveScreen(self, "participateEvent_1")
    self.driver.find_element(By.ID, "btn_event_participate_unset").click()
    saveScreen(self, "participateEvent_2")

def cancleEvent(self):
    saveScreen(self, "cancleEvent_0")
    self.driver.find_element(By.ID, "btn_event_cancle_set").click()
    saveScreen(self, "cancleEvent_1")
    self.driver.find_element(By.ID, "btn_event_cancle_unset").click()
    saveScreen(self, "cancleEvent_2")

def deleteEvent(self):
    saveScreen(self, "deleteEvent_0")
    self.driver.find_element(By.ID, "btn_event_cancle_set").click()
    saveScreen(self, "deleteEvent_1")
    self.driver.find_element(By.ID, "btn_event_delete").click()
    alert = self.driver.switch_to.alert
    #saveScreen(self, "deleteEvent_2")
    alert.accept()
    saveScreen(self, "deleteEvent_3")
    self.driver.switch_to.parent_frame

# def initDriverChrome():
#     from selenium.webdriver.chrome.options import Options
#     chrome_options = Options()
#     #chrome_options.add_argument("--lang=en")
#     chrome_options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
#     chrome_options.add_argument("--lang=en")
#     driver = webdriver.Chrome(options=chrome_options)
#     driver.maximize_window()
#     driver.get("http://127.0.0.1:8000")
#     driver.maximize_window()
#     driver.implicitly_wait(3)
#     return driver

def initDriver(language = "en"):
    fo = webdriver.FirefoxOptions();
    fo.set_preference("intl.accept_languages", language)
    #fo.set_preference("layout.css.devPixelsPerPx", str(0.5))
    driver = webdriver.Firefox(fo)
    driver.get("http://127.0.0.1:8000")
    driver.maximize_window()
    driver.implicitly_wait(3)
    return driver

usr = "Nutzer"
adm = "Admin"
pwd = "BananeZauberWelt"
mail = "gilbert@erlangen.ccc.de"

class WebInterface(unittest.TestCase):
    language = "en"

    @classmethod
    def setUpClass(self):
        if len(sys.argv) > 1:
          self.language = sys.argv[1]
        self.server = runServer()
        self.driver = initDriver(self.language)

    def test_0_create_normal_user(self):
        register(self, usr, pwd, mail, "Deutsch")
        logout(self)

    def test_1_login_logout_normal_user(self):
        login(self, usr, pwd)
        logout(self)

    def test_2_make_admin(self):
        register(self, adm, pwd, mail, "Englisch")
        logout(self)
        makeAdmin(adm)

    def test_3_login_logout_admin(self):
        login(self, adm, pwd)
        logout(self)

    def test_4_create_typs(self):
        login(self, adm, pwd)
        newType(self, "Freies Training")
        newType(self, "Handstandkurs")
        newType(self, "Akrobatik für Anfänger")
        logout(self)

    def test_5_create_events(self):
        login(self, adm, pwd)
        newEvent(self, "11:00", "14:00")
        newEvent(self,"19:00", "23:00")
        logout(self)

    def test_6_modify_event(self):
        login(self, adm, pwd)
        modifyEvent(self, "10:00", "14:00")
        logout(self)

    def test_7_participate_event(self):
        login(self, adm, pwd)
        participateEvent(self)
        logout(self)

    def test_8_cancle_event(self):
        login(self, adm, pwd)
        cancleEvent(self)
        logout(self)

    def test_9_delete_event(self):
        login(self, adm, pwd)
        deleteEvent(self)
        logout(self)

    @classmethod
    def tearDownClass(self):
        self.driver.quit()
        self.server.terminate()

if __name__ == '__main__':
    langs = ["en", "de"]
    if len(sys.argv) != 2:
        sys.exit("Specify language code on commandline: " + ", ".join(langs))
    WebInterface.language = sys.argv[1]
    if WebInterface.language not in langs:
        sys.exit("Require one of following lang codes: " + ", ".join(langs))
    del sys.argv[1:]
    unittest.main()