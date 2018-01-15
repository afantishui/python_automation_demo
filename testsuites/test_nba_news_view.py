import time
import unittest
import sys
sys.path.append("..")
from framework.browser_engine import BrowserEngine
from pageobjects.baidu_homepage import HomePage
from pageobjects.baidu_news_home import NewHomePage
from pageobjects.news_sport_home import SportNewsHomePage 

class ViewNBANews(unittest.TestCase):
	def setUp(self):
		browse = BrowserEngine(self)
		self.driver = browse.open_browser(self)

	def tearDown(self):
		self.driver.quit()

	def test_view_nba_views(self):
		baiduhome = HomePage(self.driver)
		baiduhome.click_news()
		newshome = NewHomePage(self.driver)
		newshome.click_sports()
		sportnewhome = SportNewsHomePage(self.driver)
		sportnewhome.click_nba_link()
		sportnewhome.screenshot()

if __name__ == '__main__':
	unittest.main()