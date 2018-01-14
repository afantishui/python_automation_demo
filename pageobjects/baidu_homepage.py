import sys
sys.path.append("..")
from framework.base_page import BasePage

class HomePage(BasePage):
	input_box = "xpath=>//*[@id='kw']"
	search_submit_btn = "xpath=>//*[@id='su']"
	news_link = "xpath=>//*[@id='u1']/a[1]"


	def type_search(self,text):
		self.type(self.input_box,text)

	def send_submit_btn(self):
		self.click(self.search_submit_btn)

	def click_news(self):
		self.click(self.news_link)
		self.sleep(2)

	def move_to_element(self):
		self.scrollToElement(self.find_element(self.search_submit_btn))
