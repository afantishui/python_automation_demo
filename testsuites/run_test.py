#coding = utf-8
import unittest
import sys
sys.path.append("..")
from framework.browser_engine import BrowserEngine
#from framework.excelManage import AutoForm
import HTMLTestRunner
import os
import time

'''
配置用例文件名list及浏览器配置
'''
TESTFILE_LIST=[u"TEST_MIC登录.xlsm",u"TEST_百度搜索.xlsm"]
THIS_DIR = os.path.dirname(__file__)
def getAbsPath(relativePath):
	return os.path.join(THIS_DIR,relativePath)

class RunTest(unittest.TestSuite):
	@classmethod
	def setUpClass(cls):
		#实例化
		browser = BrowserEngine
		cls.driver = browser.open_browser(cls)
		cls.af = AutoForm(cls.driver)

	# arg1 文件名 arg2 用例名
	def action(self,arg1,arg2):
		filePath = getAbsPath("testcases" + "\\" + arg1) #获取路径
		caseName = arg2
		res      = self.af.runCase(filePath,caseName,logsDir = getAbsPath("logs"))
		state    = True
		info     = ""
		for i in range(0,res.__len__()):
			state = state and res.__getitem__(i).get("state")
			info = info + res.__getitem__(i).get("title") + ":" + res.__getitem__(i).get("info")
		print(u"用例集文件:" + filePath + "" + u"用例:" + caseName)
		print(info)
		self.assertEqual(True,state)

	@staticmethod
	# arg1 文件名 arg2 用例名
	def getTestFunc(arg1,agr2):
		def func(self):
			self.action(arg1,arg2)
		return func

	@classmethod
	def tearDownClass(cls):
		cls.driver.quit()

#获取TestSuite
def getTestSuite(*classes):
	valid_type = (unittest.TestSuite,unittest.TestCase)
	suite = unittest.TestSuite() #创建测试套件
	for cls in classes:
		#isinstance判断一个对象是否是一个已知的类型
		if isinstance(cls,str):
			#sys.modules 全局字典
			if cls in sys.modules: 
				suite.addTest(unittest.findTestCases(sys.modules[cls]))
			else:
				raise ValueError("str arguments must be keys in sys.modules")
		elif isinstance(cls,valid_type):
			suite.addTest(cls)#将测试用例添加到测试套件中
		else:
			suite.addTest(unittest.makeSuite(cls))

	return suite

def __generateTestCases():
	TESTFILE_LIST = []
	index = 0
	for i in range(TESTFILE_LIST.__len__()):
		t_fileName = TESTFILE_LIST.__getitem__(i)
		t_filePath = getAbsPath("testcases" + "\\" + t_fileName )
		t_caseList = AutoForm.getTestSuiteFromStdExcel(t_filePath)
		for j in range(t_caseList.__len__()):
			TESTFILE_LIST.append((str(index),t_fileName,t_caseList.__getitem__(j)))
			index = index + 1
	arglists = TESTFILE_LIST
	for args in arglists:
		# setattr()增加或设置对象object一个属性名称name，并设置相应的值value
		setattr(RunTest,"test_func_%s"%(args[0]),RunTest.getTestFunc(args[1],args[2]))

__generateTestCases()


if __name__ == '__main__':
	testSuite = getTestSuite(RunTest)
	reportFile = os.path.dirname(os.path.abspath('.')) + '/test_report/'
	now = time.strftime("%Y-%m-%d-%H_%M_%S",time.localtime(time.time()))
	#设置报告名称格式
	HtmlFile = reportFile + now + "HTMLtemplate.html"
	print(HtmlFile)
	fp=open(HtmlFile,"wb")
	runner = HTMLTestRunner.HTMLTestRunner(stream = fp,title = u"XX项目测试报告", description=u"用例测试情况") #初始化实例测试执行器
	runner.run(testSuite)
	print("OK")