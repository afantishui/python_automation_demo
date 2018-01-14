#-*- coding: utf-8 -*-
import os,time,re
import subprocess

class AndroidBaseOperation(object):

	def get_pid(self,pak_name):
		cmd = "adb shell ps | grep " + pak_name
		output = subprocess.check_output(cmd).decode()
		#print(output)
		if output == "":
			return "the process doesn't exist"
		result = output.split()
		return result[1]


	#获取设备信息 系统版本号 手机品牌 手机名
	def getModel(self):	
		cmd = "adb shell cat /system/build.prop"
		cmd1 = "adb shell getprop ro.product.model"
		output = subprocess.check_output(cmd).decode()
		And_version = re.findall("version.release=(\d\.\d)*",output,re.S)[0] #  Android 系统  #re.S  表示“.”的作用扩展到整个字符串，包括“\n”
		phone_model = re.findall("ro.product.brand=(\S+)*",output,re.S)[0]#手机品牌
		phone_name  = os.popen(cmd1).read().strip()
		return And_version,phone_model,phone_name
		#这里取设备信息使用了两种不同的方法，是因为用subprocess拿设备名时拿不到空格后面的名称，
		#改用os.popen后续可优化正则进行匹配

	#获取内存信息
	def getMeminfo(self,pak_name):
		cmd = "adb shell dumpsys meminfo %s" %(pak_name)
		output = subprocess.check_output(cmd).split()
		s_mem = ".".join([x.decode() for x in output]) #转换为string
		s_mem2 = int(re.findall("TOTAL.(\d+)*",s_mem,re.S)[0])

		print(s_mem2)
		return s_mem2

	#获取CPU核数
	def get_cpu_kel(self,devices):
		cmd = "adb -s " + devices + " shell cat /proc/cpuinfo"
		#print(cmd)
		output = subprocess.check_output(cmd).split()
		sitem = ".".join([x.decode() for x in output])
		cpu_kel = len(re.findall("processor",sitem))
		print(cpu_kel)
		return cpu_kel

	#获取CPU使用情况
	'''获取cpu快照'''
	def totalCpuTime(self,devices):
		user = nice = system = idle = iowait = irq = softirq = 0
		'''
		user:从系统启动开始累计到当前时刻，处于用户态的运行时间，不包含 nice值为负进程。
    	nice:从系统启动开始累计到当前时刻，nice值为负的进程所占用的CPU时间
    	system 从系统启动开始累计到当前时刻，处于核心态的运行时间
    	idle 从系统启动开始累计到当前时刻，除IO等待时间以外的其它等待时间
    	iowait 从系统启动开始累计到当前时刻，IO等待时间(since 2.5.41)
    	irq 从系统启动开始累计到当前时刻，硬中断时间(since 2.6.0-test4)
    	softirq 从系统启动开始累计到当前时刻，软中断时间(since 2.6.0-test4)
    	stealstolen  这是时间花在其他的操作系统在虚拟环境中运行时（since 2.6.11）
    	guest 这是运行时间guest 用户Linux内核的操作系统的控制下的一个虚拟CPU（since 2.6.24）
		'''
		cmd = "adb -s " + devices + " shell cat /proc/stat"
		#print(cmd)
		p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
		(output, err) = p.communicate()
		res = output.split()

		for info in res:
			if info.decode() == "cpu":
				user    = res[1].decode()
				nice    = res[2].decode()
				system  = res[3].decode()
				idle    = res[4].decode()
				iowait  = res[5].decode()
				irq     = res[6].decode()
				softirq = res[7].decode()
				#print("user=" + user)
				#print("nice=" + nice)
				#print("system=" + system)
				#print("idle=" + idle)
				#print("iowait=" + iowait)
				#print("irq=" + irq)
				#print("softirq=" + softirq)
				result = int(user) + int(nice) + int(system) + int(idle) + int(iowait) + int(irq) + int(softirq)
				#print("totalCpuTime: " + str(result))
				return result

	'''
	每一个进程快照
	'''
	def processCpuTime(self,pid,devices):
		'''
		pid 	进程号
		utime   该任务在用户态运行的时间，单位为jiffies
    	stime   该任务在核心态运行的时间，单位为jiffies
    	cutime  所有已死线程在用户态运行的时间，单位为jiffies
    	cstime  所有已死在核心态运行的时间，单位为jiffies
		'''
		utime = stime = cutime = cstime = 0
		cmd = "adb -s " + devices + " shell cat /proc/" + pid + "/stat"
		#print(cmd)
		p = subprocess.Popen(cmd, stdout = subprocess.PIPE, stderr = subprocess.PIPE, shell = True)
		(output,err) = p.communicate()
		res = output.split()
		utime = res[13].decode()
		stime = res[14].decode()
		cutime = res[15].decode()
		cstime = res[16].decode()
		#print("utime="+ utime)
		#print("stime="+ stime)
		#print("cutime="+ cutime)
		#print("cstime="+ cstime)
		result = int(utime) + int(stime) + int(cutime) + int(cstime)
		#print("ProcessCpuTime=" + str(result))
		return result
	'''
	计算某进程的cpu使用率
	100*( processCpuTime2 – processCpuTime1) / (totalCpuTime2 – totalCpuTime1) (按100%计算，如果是多核情况下还需乘以cpu的个数);
	cpukel cpu几核
	pid 进程id
	'''
	def cup_rate(self,pid,cpukel,devices):
		processCpuTime1 = self.processCpuTime(pid,devices)
		totalCpuTime1 = self.totalCpuTime(devices)
		time.sleep(20)
		processCpuTime2 = self.processCpuTime(pid,devices)
		processCpuTime3 = processCpuTime2 - processCpuTime1
		print("processCpuTime3:%s"%processCpuTime3)


		#time.sleep(5)
		totalCpuTime2 = self.totalCpuTime(devices)
		totalCpuTime3 = (totalCpuTime2 - totalCpuTime1)*cpukel
		print("totalCpuTime3:%s" %totalCpuTime3)

		cpu = 100 * (processCpuTime3) / (totalCpuTime3)
		print(cpu)


	#获取电池电量
	def get_battery(self,devices):
		cmd = "adb -s " + devices + " shell dumpsys battery"
		print(cmd)
		output = subprocess.check_output(cmd).split()
		st = ".".join([x.decode() for x in output]) # 转换为string
		battery2 = int(re.findall("level:.(\d+)*", st, re.S)[0])
		print(battery2)
		return battery2

	#获取上下行流量
	def get_flow(self,pid, type, devices):
		# pid = get_pid(pkg_name)
		_flow1 = [[], []]
		if pid is not None:
			cmd = "adb -s " + devices + " shell cat /proc/" + pid + "/net/dev"
			print(cmd)
			_flow = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
										stderr=subprocess.PIPE).stdout.readlines()
			for item in _flow:
				if type == "wifi" and item.split()[0].decode() == "wlan0:":  # wifi
					# 0 上传流量，1 下载流量
					_flow1[0].append(int(item.split()[1].decode()))
					_flow1[1].append(int(item.split()[9].decode()))
					print("------flow---------")
					print(_flow1)
					break
				if type == "gprs" and item.split()[0].decode() == "rmnet0:":  # gprs
					print("-----flow---------")
					_flow1[0].append(int(item.split()[1].decode()))
					_flow1[1].append(int(item.split()[9].decode()))
					print(_flow1)
					break
		else:
			_flow1[0].append(0)
			_flow1[1].append(0)

#a = AndroidBaseOperation()
#a.get_battery("c5306b75")
#a.get_flow("758","wifi","c5306b75")
#cpukel = a.get_cpu_kel("c5306b75")
#a.totalCpuTime("c5306b75")
#pid = a.get_pid("wuyichuanqi")
#a.cup_rate(pid,cpukel,"c5306b75")
