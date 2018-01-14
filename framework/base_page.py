import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import os.path
import sys
sys.path.append("..")
from lib.logger import Logger

logger = Logger(logger="BasePage").getlog()

class BasePage(object):
	"""定义一个页面基类，让所有页面都继承这个类，封装一些常用的页面操作方法到这个类"""
	def __init__(self, driver):	
		#构造函数
		self.driver = driver

	#关闭浏览器
	def quit_browser(self):
		logger.info("Close and Quit the browser.")
		self.driver.quit()

	# 浏览器前进操作
	def forward(self):
		self.driver.forward()
		logger.info("Click forward on current page.")

	# 浏览器后退操作
	def back(self):
		self.driver.back()
		logger.info("Click back on current page.")

	# 隐式等待
	def wait(self,seconds):
		self.driver.implicitly_wait(seconds)
		logger.info("wait for %d seconds." % seconds)

	# 点击关闭当前窗口
	def close(self):
		try:
			self.driver.close()
			logger.info("Closing and quit the browser.")
		except NameError as e:
			logger.error("Failed to quit the browser with %s" % e)

	#保存截图
	def screenshot(self):
		#在这里我们把file_path这个参数写死，直接保存到我们项目根目录的一个文件夹.\Screenshots下
		file_path = os.path.dirname(os.path.abspath('.')) + '/screenshot/'
		rq = time.strftime('%Y%m%d%H%M',time.localtime(time.time()))
		screen_name = file_path + rq + '.png'
		try:
			#截图三种方法
			#self.driver.get_screenshot_as_base64()
			#self.driver.get_screenshot_as_png()
			self.driver.get_screenshot_as_file(screen_name)
			logger.info("Had take screenshot and save to folder:/screenshots")
		except Exception as e:
			logger.error("Failed to take screenshot! %s" % e)
			self.screenshot()

	#查找元素
	def find_element(self,selector):
		element = ' '
		if '=>' not in selector:
			return self.driver.find_element_by_id(selector)
		selector_by = selector.split('=>')[0]
		selector_value = selector.split('=>')[1]
		#print(selector_by,selector_value)

		if selector_by == 'i' or selector_value == 'id':
			try:
				element = self.driver.find_element_by_id(selector_value)
				logger.info("Had find the element %s successful"
        					"by %s via value:%s" % (element.text,selector_by,selector_value))
			except NoSuchElementException as e:
				logger.info("NoSuchElementException:%s" % e)
				self.screenshot()
		elif selector_by == 'n' or selector_by == 'name':
			element = self.driver.find_element_by_name(selector_value)
		elif selector_by == 'c' or selector_by =='class_name':
			element = self.driver.find_element_by_class_name(selector_value)
		elif selector_by == 'l' or selector_by =='link_text':
			element = self.driver.find_element_by_link_text(selector_value)
		elif selector_by == 'p' or selector_by == 'partial_link_text':
			element = self.driver.find_element_by_partial_link_text(selector_value)
		elif selector_by == 't' or selector_by == 'tag_name':
			element = self.driver.find_element_by_tag_name(selector_value)
		elif selector_by == 'x' or selector_by == 'xpath':
			try:
				element = self.driver.find_element_by_xpath(selector_value)
				logger.info("Had find the element \'%s\'successful"
        					"by %s via value:%s" % (element.text,selector_by,selector_value))
			except NoSuchElementException as e:
				logger.info("NoSuchElementException:%s" % e)
				self.screenshot()
		elif selector_by == 's' or selector_by == 'selector_selector':
			element = self.driver.find_element_by_css_selector(selector_value)
		else:
			raise NameError("请输入一个有效的目标元素类型.")

		return element

	
	#输入
	def type(self,selector,text):
		el = self.find_element(selector)
		el.clear()
		try:
			el.send_keys(text)
			logger.info("Had type \'%s\' in inputBox" % text)
		except NameError as e:
			logger.error("Failed to type in inputBox with %s" %e)
			self.screenshot()

	#清除文本
	def clear_text(self,selector):
		el = self.find_element(selector)
		try:
			el.clear()
			logger.info("Clear text in inputBox before typeing.")
		except NameError as e:
			logger.error("Failed to clear in inputBox with %s" % e)
			self.screenshot()

	#点击
	def click(self,selector):
		el = self.find_element(selector)
		text = el.text
		#print(el.text)
		try:
			el.click()
			logger.info("The element \'%s\' was clicked." % text)
		except NameError as e:
			logger.error('Failed to click the element with %s' % e)

	#获得标题
	def get_page_title(self):
		logger.info("Current page title is %s" % self.driver.title)
		return self.driver.title

	#获得页面URL
	def get_url(self):
		logger.info("URL:%s" % self.driver.current_url)
		return self.driver.current_url

	#获取浏览器版本
	def get_browser_version(self):
		logger.info("Current browser version is %s" % self.driver.capabilities['version'])
		return self.driver.capabilities['version']

	#打开新页面 谷歌浏览器无效
	def open_new_page(self):
		ele = self.driver.find_element_by_name('body').send_keys(Keys.CONTROL + 't')
		logger.info("open a new page successful.")

	#打印页面所有href
	def get_all_href(self):
		link_list = []
		for link in self.driver.find_elements_by_xpath("//*[@href]"):
			link_list.append(link.get_attribute('href'))
			print(link.get_attribute('href'))
		#print(link_list)

	#获取打印时间
	def get_time(self):
		now_time = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) # 格式化时间，按照 2017-04-15 13:46:32的格式打印出来
		print(now_time)

	@staticmethod   #@staticmethod不需要表示自身对象的self和自身类的cls参数，就跟使用函数一样
	def sleep(seconds):
		time.sleep(seconds)
		logger.info("Sleep for %d seconds" % seconds)

	def scrollToElement(self,element):
		try:
			scrollto = "window.scrollTo(" + str(element.location.get("x")) + "," + str(
				element.location.get("y")) + ")"
			self.driver.execute_script(scrollto)
			logger.info("scrollToElement")
		except Exception as e:
			print(e)
