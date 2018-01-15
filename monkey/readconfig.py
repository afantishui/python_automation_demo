# -*- coding:utf-8 -*-
import sys,xlrd,xlsxwriter,os,time,datetime

def getdata_excel():
	filepath = '..\\testcases\\monkey.xlsx'
	file	 = xlrd.open_workbook(filepath) #打开Excel
	excel 	 = file.sheets()[0]     #实例Excel表
	ncols 	 = excel.ncols			#获取表列数
	case_list= []				#存放命令行数组
	
	#读取Excel的配置
	for i in range(1,ncols):
		case = excel.cell(1,i).value
		if case != 'null':
			case_list.append(case)
		else:
			continue

	#拼接语句
	case1 = case_list[1]
	for i in range(2,len(case_list)-1):
		case1 = str(case1) +' '+ str(case_list[i])
	case1 = case1 +' '+str(int(case_list[len(case_list)-1]))  #这里单独写是因为Excel的数字读出来是浮点型，在for循环不好处理
	return case1  #返回完整语句

def run_shell():
	case = getdata_excel()
	path      = os.path.dirname(os.path.abspath('.')) #保存报告的相对路径
	day  = time.strftime("%Y%m%d%H%M", time.localtime(time.time())) #获取日期
	info_log = '%s-monkey-info.txt'%day
	logpath1 = path+'\\logs\\'+ info_log
	cmd = 'adb shell monkey -p'+' '+case + ' 1>' + logpath1 + ' 2>&1 &' 
	return cmd,logpath1,info_log