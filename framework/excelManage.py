# coding = utf-8
import xlrd
import datetime
import re,os,sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from browser_engine import BrowserEngine

ctype = {0:"empty",1:"string",2:"number",3:"data",4:"boolean",5:"error"}

class ExcelManage(object):
	def __init__(self,filepath):
		self.filepath = filepath #定义文件路径
		self.workbook = xlrd.open_workbook(filename = self.filepath) #定义工作表

	def setFilePath(self,filepath):
		self.filepath = filepath
		self.workbook = xlrd.open_workbook()

	'''
	将excel中的内容转换为字符串
	注:boolean类型，true转为"1",false转为"0"
	ctype = {0:"empty",1:"string",2:"number",3:"data",4:"boolean",5:"error"}
	'''
	def getDataInString(self,book,cell):
		cell_ctype = cell.ctype
		if cell_ctype == 0:
			return ""
		elif cell_ctype == 1:
			return cell.value
		elif cell_ctype == 2:
			num_value = cell.value
			if int(num_value) == num_value:
				return str(int(num_value))
			else:
				return str(num_value)
		elif cell_ctype == 3:
			#把时间转化为元组形式，如2017/9/9转成(2017,9,9,0,0,0)
			date_value = xlrd.xldate_as_tuple(cell.value,book.datemode)
			if(date_value[3:]) == (0,0,0):
				#函数接收元组或字典形式的参数 的时候，使用*前缀，date_value已转化为元组
				return datetime.date(*date_value[:3]).strftime("%Y-%m-%d")
			else:
				return datetime.datetime(*date_value).strftime("%Y-%m-%d %H:%M:%S")
		elif cell_ctype == 4:
			return str(cell.value)
		elif cell_ctype == 5:
			return ""
		else:
			return str(cell.value)

	'''
	读取某一sheet页,某行数据
	参数：sheet页名称,行索引(从0开始),列开始索引(从0开始),数据长度
	'''
	def getDatasByRow(self,sheetName,rowNum,sNum,len):
		book = self.workbook
		try:
			sheet = book.sheet_by_name(sheetName)
		except:
			print("no sheet in %s named %s" % (self.filepath,sheetName))
			return
		dataList = []
		maxLen = sheet.row(rowNum).__len__() #获取元素个数
		for i in range(sNum,sNum + len):
			if(i <= maxLen - 1):
				cellOri = sheet.cell(rowNum,i) #cell(x,y)返回所引用单元格的格式、位置或内容等信息
				if(cellOri.ctype == 5):
					print("cell(%d,%d) in sheet(%s) in file(%s) is error" % rowNum,i,sheetName,self.filepath)
					dataList.append("")
				else:
					dataList.append(self.getDataInString(book,cellOri))
			else:
				dataList.append("")
		return dataList

	'''
    读取某一sheet页,某列数据
    参数：sheet页名称(从0开始),列索引(从0开始),行开始索引(从0开始),数据长度
    '''
	def getDatasByCol(self,sheetName,colNum,sNum,len):
		book = self.workbook
		try:
			sheet = book.sheet_by_name(sheetName)
		except:
			print("no sheet in %s named %s" % (self.filepath,sheetName))
			return
		dataList = []
		maxLen = sheet.col(colNum).__len__()
		for i in range(sNum,sNum + len):
			if(i <= maxLen - 1):
				cellOri = sheet.cell(i,colNum)
				if(cellOri.ctype == 5):
					print ("cell(%d,%d) in sheet(%s) in file(%s) is error")
					dataList.append("")
				else:
					dataList.append(self.getDataInString(book,cellOri))
			else:
				dataList.append("")
		return dataList
	'''
	从某列中找到第一个满足的字符串返回序列号
	'''
	def getIndexByCol(self,sheetName,colNum,dist):
		book = self.workbook
		try:
			sheet = book.sheet_by_name(sheetName)
		except:
			print("no sheet in %s named %s" % (self.filepath,sheetName))
			return 9999 #9999表示没找到
		size = sheet.col(colNum).__len__()
		for i in range(0,size):
			cellStr = self.getDataInString(book,sheet.cell(i,colNum))
			if (cellStr == dist):
				return i
			else:
				continue
		return 9999#表示没找到

	'''
	从某行中找到第一个满足的字符串返回序列号
	'''
	def getIndexByRow(self,sheetName,rowNum,dist):
		book = self.workbook
		try:
			sheet = book.sheet_by_name(sheetName)
		except:
			print("no sheet in %s named %s" % (self.filepath,sheetName))
			return 9999#表示没找到
		size = sheet.row(rowNum).__len__()
		for i in range(0,size):
			cellStr = self.getDataInString(book,sheet.cell(i,rowNum))
			if (cellStr == dist):
				return i
			else:
				continue
		return 9999#表示没找到

	def closeExcel(self):
		self.workbook = None

#----------------------------------------------#

#----------------------------------------------#
class AutoForm(object):
	def __init__(self,browser):
		self.YES       = "yes"
		self.NO        = "no"
		self.SPLITMARK = "###"
		self.XPATHARG  = "{@@}"
		self.driver    = browser.open_browser()

	'''
	读取指定格式的datas，完成指定操作
	datas格式要求如下：
	datas=[
	{"xpath":"","op":"get","value":""},
	{"xpath":"//input[@id='logonInfo.logUserName']","op":"sendKeys","value":"dongfang"}
	]
	'''
	def fixTheForm(self,title,datas,logDir=None,filePath=None,defaultParams=None):
		params = {}  #{}代表dict字典数据类型，字典是由键对值组组成。冒号':'分开键和值，逗号','隔开组
		if(defaultParams != None and defaultParams.__len__()>0):
			for (k,v) in defaultParams.items():
				params.__setitem__(k,v)

		result = {"state": True, "info": self.getNowStrftime(),"title":">>>"+title}
		for i in range(datas.__len__()):
			tmp = datas.__getitem__(i)
			_op=tmp.get("op").lower()
			_xpath=tmp.get("xpath")
			_value=tmp.get("value")
			if(_op=="skip"):
				continue

			#处理保存参数操作,value是个有返回值的js语句
			pattern1=re.compile(r"\{@(\w+)@\}")
			m1=pattern1.match(_op)
			if(m1):
				try:
					ret=str(self.driver.execute_script(_value))
					self.driver.implicitly_wait(2)
					params.__setitem__(m1.group(1),ret)
					t_result = {"state": True, "info": ""}
					result = self.mergeResult(result,t_result)
					continue
				except Exception as e:
					t_result = {"state": False, "info": getErrInfo(_xpath,"executeJs",_value,str(e))}
					result = self.mergeResult(result,t_result)
					continue

			#处理带参数的xpath
			if (_xpath.__contains__(self.XPATHARG) and _value.__contains__(self.SPLITMARK)):
				indx = _value.find(self.SPLITMARK)
				xpathParm = _value[:indx]
				_xpath = _xpath.replace(self.XPATHARG,xpathParm)
				_value = _value[indx + self.SPLITMARK.__len__():]

			#处理value中含有参数
			pattern2=re.compile(r".*\{@(\w+)@\}.*")
			c = 0
			while pattern2.match(_value) and c<100:  #防止无限循环
				m2 = pattern2.match(_value)
				t_key = m2.group(1)
				c = c + 1
				if(params.has_key(t_key)):
					_value=_value.replace("{@"+t_key+"@}",params.get(t_key))
				else:
					_value==_value.replace("{@"+t_key+"@}","{"+t_key+"}")

			#处理调用公共步骤
			if(_op=="call" and filePath!=None):
				dParams={}
				tValues=_value.split(self.SPLITMARK)
				if(tValues.__len__()>1):
					for i in range(1,tValues.__len__()):
						tParamValue=tValues[i].split("=")
						dParams.__setitem__(tParamValue[0],tParamValue[1])
				t_result=self.runSteps(filePath,tValues[0],None,dParams).__getitem__(0)
				t_result.__setitem__("info",u"第"+str(i+1)+u"步调用公共步骤"+_value+":"+t_result.get("info"))
				result = self.mergeResult(result,t_result)
				continue

			#处理上传\比较下载文件操作的相对链接
			if((_op=="upload" or _op=="sameaslocalfile") and (not _value.__contains__(":"))):
				if(logDir!=None):
					_value=os.path.join(os.path.dirname(logDir),_value)
				else:
					print ("can't find the logs dir,can't use the relative path")

			#处理正常操作
			t_result = self.doOperate(_op,_xpath,_value)
			if(not t_result.get("state")):
				if((_xpath or "").__len__()>0 and
						BrowserManage.isElementPresent(self.driver,By.XPATH,_xpath)):
					BrowserManage.scrollToElement(self.driver,self.driver.find_element_by_xpath(_xpath))
				if(logDir!=None):
					snapFile=os.path.join(logDir,self.getNowStrftime2()+".png")
					self.driver.get_screenshot_as_file(snapFile)
					snapInfo="<img src=\"file:\\\\\\"+os.path.abspath(snapFile).strip()+"\" height=\"600\" width=\"800\">"
				else:
					print ("can't find the logs dir,can't use the relative path")
					snapInfo=""
				t_result.__setitem__("info",u"第"+str(i+1)+u"步:"+t_result.get("info")+u"\n截图:\n"+snapInfo+"\n")
				result = self.mergeResult(result,t_result)
		if(result.get("state")):
			result.__setitem__("info",result.get("info")+" PASS\n")
		return result
	'''
	解析指定格式数据，将其解析成fixTheForm需要的数据
	originDatas的格式(元素名称)如下：
	'''
	def parseDateFromStdExcel(self,filePath,sheetName):
		#em excelmanage
		em = ExcelManage(filepath)
		dataStepSize  = int(em.getDatasByCol(sheetName,1,0,1)[0])
		dataGroupSize = int(em.getDatasByCol(sheetName,2,0,1)[0])
		xpath_array   = self.getXpathArrayFromStdExcel(filename,sheetName,dataStepSize)
		datas = []
		i = 0
		while (i < dataStepSize):
			piece = None
			runState = self.YES
			isRun = em.getDatasByCol(sheetName,3+2*i,0,1)[0]
			if(isRun == u"忽略" or isRun == ""):
				runState = self.NO
			title       = em.getDatasByCol(sheetName,4+2*i,0,1)[0]
			op_array    = em.getDatasByCol(sheetName,3+2*i,2,dataStepSize)
			value_array = em.getDatasByCol(sheetName,4+2*i,2,dataStepSize)
			piece       = (runState,title,self.mergeInputDatas(xpath_array,op_array,value_array)) #元组数据类型
			datas.append(piece)
			i = i+1
		em.closeExcel()
		return datas

	#获取xpathArray
	def getXpathArrayFromStdExcel(self,filepath,sheetName,dataSize):
		em = ExcelManage(filePath)
		sheetNames = em.getDatasByCol(sheetName,1,2,dataSize) #表名
		elementNames = em.getDatasByCol(sheetName,2,2,dataSize) #元素名
		xpath_array = []
		for i in range(0,dataSize):
			#strip(rm) 删除字符串开头、结尾，位于rm的字符，为空是删除空白符
			t_sheetName = sheetNames[i].strip()
			t_elementName = elementNames[i].strip()
			idx = em.getIndexByCol(t_sheetName,1,t_elementName) 
			xpath_array.append(em.getDatasByCol(t_sheetName,2,idx,1)[0])
		return xpath_array
	'''
	合并xpath数组，操作数组，值数组.
	构成字典列表
	'''
	def mergeInputDatas(self,xpath_array,op_array,value_array):
		length = xpath_array.__len__() #xpath的长度
		inputDatas = []
		for i in range(0,length):
			t_op    = ""
			t_value = ""
			if (i >= op_array.__len__()):
				t_op = ""
			else:
				t_op = op_array[i]
			if (i >= value_array.__len__()):
				t_value = ""
			else:
				t_value = value_array[i]
			inputDatas.append({"xpath":xpath_array[i],"op":t_op,"value":t_value})
		return inputDatas

	#运行指定格式sheet页面的测试用例
	def runCase(self,filePath,sheetName,logsDir = None):
		datas      = self.parseDateFromStdExcel(filepath,sheetName)
		resultList = []
		for i in range(0,datas.__len__()):
			piece = datas.__getitem__(i)
			runState = piece[0]
			if (runState == self.NO):
				continue
			else:
				title      = piece[1]
				inputDatas = piece[2]
			t_result = self.fixTheForm(title,inputDatas,logDir = logsDir,filePath=filePath)
			resultList.append(t_result)
		return resultList
	'''
	运行指定格式sheet页中的测试用例
	'''
	def runSteps(self,filePath,sheetName,logsDir=None,dParams=None):
		datas      = self.parseDateFromStdExcel(filePath,sheetName)
		resultList = []
		for i in range(0,datas.__len__()):
			piece    = datas.__getitem__(i)
			runState = piece[0]
			if(runState==self.NO):
				continue
			else:
				title = piece[i]
				inputDatas = piece[2]
			t_result = self.fixTheForm(title,inputDatas,logDir=logsDir,filePath=filePath,defaultParams=dParams)
			resultList.append(t_result)
		return resultList

	#获取指定格式Excel中测试集
	@staticmethod
	def getTestSuiteFromStdExcel(filePath):
		em = ExcelManage(filepath)
		caseCount = int(em.getDatasByCol(u'配置',3,0,1)[0])
		caseArray = em.getDatasByCol(u"配置",2,2,caseCount)
		stateArray = em.getDatasByCol(u"配置",3,2,caseCount)
		runCaseList = []
		for i in range(0,caseCount):
			if (stateArray[i] != u"忽略"):
				runCaseList.append(caseArray[1])
		return runCaseList


if __name__ == '__main__':

	file = u"C:/Users/37/Desktop/test/py/automation_framework_demo/testcases/TEST_MIC登录.xlsm"
	#TEST_MIC登录.xlsm
	print(file)
	em = ExcelManage(file)
	#print (em.getDatasByCol(u"配置",3,1,5))
	#print (em.getDatasByRow(u"配置",2,1,5))
	print (em.getDatasByRow(u"CASE_登录必填检查",6,0,1))
	print (em.getDatasByRow(u"CASE_登录必填检查",5,0,2))
	print (em.getDatasByCol(u"CASE_登录必填检查",1,0,1)[0])
	print (em.getDatasByRow(u"配置",3,2,2))
	t_caseList = af.getTestSuiteFromStdExcel(file)
	print(t_caseList.__len__())
	#rint (em.getDatasByCol(u"CASE_搜索关键词",3,1,5)[0]==u"元素XPATH(此列拖拽后不要清除)")
	#print (em.getDatasByRow(u"DDD",1,3,3))