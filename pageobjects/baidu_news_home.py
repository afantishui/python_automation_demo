import sys
sys.path.append("..")
from framework.base_page import BasePage

class NewHomePage(BasePage):
	sports_link = "xpath=>//*[@id='channel-all']/div/ul/li[9]/a"

	def click_sports(self):
		self.click(self.sports_link)
		self.sleep(2)