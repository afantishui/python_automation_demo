# -*- coding:utf-8 -*-
#导入模块
import configparser #读写配置文件模块
import os.path
from selenium import webdriver
import sys
sys.path.append("..") 
from lib.logger import Logger

logger = Logger(logger="BrowserEngine").getlog()

class BrowserEngine(object):
	dir = os.path.dirname(os.path.abspath('.'))
	chrome_driver_path = dir + '/tools/chromedriver.exe'
	ie_driver_path = dir + '/tools/IEDriverServer.exe'
	
	def __init__(self, driver):
		self.driver = driver

	def open_browser(self,driver):
		config = configparser.ConfigParser()
		file_path = os.path.dirname(os.path.abspath('.')) + '/config/config.ini'
		config.read(file_path)

		browser = config.get("browserType","browserName")
		logger.info('You had select %s browser.' % browser)
		url = config.get("testServer","URL")
		logger.info("The test server url is:%s" % url)

		if browser == "Firefox":
			driver = webdriver.Firefox()
			logger.info('Starting firefox browser,version:Firefox %s' % driver.capabilities['version'])
		elif browser == "Chrome":
			driver = webdriver.Chrome(self.chrome_driver_path)
			logger.info('Starting Chrome browser,version:Chrome %s' % driver.capabilities['version'])
		elif browser == "IE":
			driver = webdriver.Ie(self.ie_driver_path)
			logger.info("Starting IE browser,version:IE %s" % driver.capabilities['version'])

		driver.get(url)
		driver.maximize_window()
		logger.info("Maximize the current window.")
		driver.implicitly_wait(10)
		logger.info("Set implicitly wait 10 seconds.")
		return driver

	def quit_browser(self):
		logger.info("now,close and quit browser")
		self.driver.quit()

print("1")
