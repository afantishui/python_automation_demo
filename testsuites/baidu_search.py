# -*- coding:utf -8 -*-
import time
import unittest
import sys
sys.path.append("..") 
from framework.browser_engine import BrowserEngine
from pageobjects.baidu_homepage import HomePage

class BaiduSearch(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		#测试固件的setUpClass代码，在所有test前运行一次
		browse = BrowserEngine(cls)
		cls.driver = browse.open_browser(cls)

	@classmethod
	def tearDownClass(cls):
		#测试固件的tearDownClass代码，在所有test后运行一次
		cls.driver.quit()

	def test_baidu_search(self):
		#开头要使用test，把测试逻辑代码封装到一个test开头的方法里
		#self.driver.find_element_by_id('kw').send_keys('selenium')
		#time.sleep(1)
		#try:
		#	assert 'selenium' in self.driver.title
		#	print ('Test Pass.')
		#except Exception as e:
		#	print('Test Fail.',format(e))
		homepage = HomePage(self.driver) #实例化
		homepage.type_search('selenium') #输入
		#homepage.send_submit_btn()		#按按钮
		#homepage.get_browser_version() #浏览器版本号
		#homepage.get_time()
		#homepage.get_all_href()
		homepage.move_to_element()
		time.sleep(5)
		#homepage.screenshot()  #截图
		'''
		try:
			assert 'selenium' in homepage.get_page_title()

			print('Test Pass')
		except Exception as e:
			print('Test Fail',format(e))
		'''
	def test_search2(self):
		homepage = HomePage(self.driver)
		homepage.type_search('python')
		homepage.send_submit_btn()
		time.sleep(2)
		#homepage.screenshot()

if __name__ == '__main__':
	unittest.main()