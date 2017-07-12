 # -*- coding: utf-8 -*-
import sys
import os
from shutil import copyfile
import urllib2
import hashlib
import shutil

_FILE_SLIM = (100*1024*1024) # 100MB

# cdn_domain = 'image.cqby.qq.com'
# dev_dir = 'test2'

cdn_domain = 'cqtxrestest.37wan.5ypy.com'
dev_dir = 'tx_dev'

CHECKIPS_FLAG = False

def file_md5(filename):
	hmd5 = hashlib.md5()
	fp = open(filename,"rb")
	f_size = os.stat(filename).st_size
	if f_size>_FILE_SLIM:
		while(f_size>_FILE_SLIM):
			hmd5.update(fp.read(_FILE_SLIM))
			f_size/=_FILE_SLIM 
		if(f_size>0) and (f_size<=_FILE_SLIM):
			hmd5.update(fp.read())
	else:
	    hmd5.update(fp.read())

	fp.close()
	
	return hmd5.hexdigest()

def errorfile(file, errmsg):
	f = open('error.txt','ab')
	f.write(file+'\t'+errmsg+'\n')
	f.close()

def requireCdnRes(logfile):
	shutil.rmtree('cdnres/', True)

	f = open(logfile, 'rb')
	while True:
		line = f.readline()
		if len(line) <= 0:
			break
		eqindex = line.find('=')
		filename = line[0:eqindex]
		md5value = line[eqindex+1:len(line)-1]

		dstdir = 'cdnres/'+filename[0:filename.rfind('/')]
		if os.path.exists(dstdir) == False:
			os.makedirs(dstdir)

		try:
			res = urllib2.urlopen('https://'+cdn_domain+'/'+dev_dir+'/'+filename)
		except Exception as e:
			print('https://'+cdn_domain+'/'+dev_dir+'/'+filename)
			errorfile('https://'+cdn_domain+'/'+dev_dir+'/'+filename, 'HTTPS ERROR')
		else:
			data = res.read()
			rf = open('cdnres/'+filename,'wb')
			rf.write(data)
			rf.close()
			res.close()

			cdnmd5 = file_md5('cdnres/'+filename)

			if cdnmd5 == md5value:
				print(filename+':\t'+cdnmd5)
			else:
				errorfile('https://'+cdn_domain+'/'+dev_dir+'/'+filename, 'MD5 ERROR')

	f.close()

def updateHost(ip):
	copyfile('hosts', 'hosts-dst')
	f = open('hosts-dst','a')
	f.write(ip + " " + cdn_domain)
	f.close()
	copyfile('hosts-dst', 'C:/Windows/System32/drivers/etc/hosts')
	os.remove('hosts-dst')

def checkips():
	if os.path.exists('error.txt') == True:
		os.remove('error.txt')
	cdmline = "nslookup "+cdn_domain + " > checkips.txt"
	os.system(cdmline)

	f = open("checkips.txt","r")
	for i in range(4):
		line = f.readline()

	if CHECKIPS_FLAG == True:
		while True:
			line = f.readline()
			line = line.replace('Addresses:  ','')
			line = line.replace('Address:  ','')
			line = line.replace('	  ','')
			line = line.replace('\n','')
			if line.find('Aliases') > -1 or len(line) <= 0:
				break
			print(line)
			updateHost(line)

			for parent,dirnames,filenames in os.walk("sourcefiles/"):
				for filename in filenames:
					requireCdnRes('sourcefiles/'+filename)
	else:
		for parent,dirnames,filenames in os.walk("sourcefiles/"):
			for filename in filenames:
				requireCdnRes('sourcefiles/'+filename)	

	f.close()

	copyfile('hosts', 'C:/Windows/System32/drivers/etc/hosts')
	os.remove('checkips.txt')

if __name__=="__main__":
	checkips()

