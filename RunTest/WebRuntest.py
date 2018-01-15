
import unittest
import HTMLTestRunner
import os
import time
import sys
sys.path.append("..")
from testsuites.baidu_search import BaiduSearch
from testsuites.test_get_page_title import GetPageTitle

#设置报告保存路径
report_path = os.path.dirname(os.path.abspath('.')) + '/test_report/'
#获取系统时间
now = time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time()))
#设置报告名称格式
HtmlFile = report_path + now + "HTMLtemplate.html"
print(HtmlFile)
fp = open(HtmlFile, "wb")
suite = unittest.TestSuite() #初始化实例一个测试套件，管理多个测试用例
suite.addTest(BaiduSearch('test_baidu_search')) #添加一个测试用例
suite.addTest(BaiduSearch('test_search2'))
suite.addTest(GetPageTitle('test_get_title'))

#2-利用makeSuite()方法，一次性加载一个类文件下所有测试用例到suite中去
#suite = unittest.TestSuite(unittest.makeSuite(BaiduSearch))

#3-利用discover（）方法去加载一个路径下所有的测试用例
#suite = unittest.TestLoader().discover("testsuites")
if __name__ == '__main__':
	runner = HTMLTestRunner.HTMLTestRunner(stream = fp,title = u"XX项目测试报告", description=u"用例测试情况") #初始化实例测试执行器
	runner.run(suite) #执行套件测试用例
