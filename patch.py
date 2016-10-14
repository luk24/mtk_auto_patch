#! /usr/bin/python
#-*-coding:utf-8-*-
import os
import commands
import sys,time
import subprocess
import threading

#text color
highline = '\033[1m'
green = '\033[1;32m'
red = '\033[1;31m'
default = '\033[0m'

global showprogress
global result
showprogress = False

def info(msg):
	print(highline + msg + default)
def error(msg):
	print(red + msg + default)

def cmdtask(cmd):
	global showprogress
	global result
	showprogress = True
	result = commands.getstatusoutput(cmd)
	showprogress = False
def progress(msg):
	global showprogress
	global result
	t = 1
	while showprogress:
		if t % 2 > 0 :
			sys.stdout.write(msg + '[\]')
		else:
			sys.stdout.write(msg + '[/]')
		sys.stdout.write('\r')
		sys.stdout.flush()
		t += 1
		time.sleep(0.5)
	if result[0] == 0:
		sys.stdout.write(msg + '[' + green + '\u2714'.encode("utf-8").decode('unicode_escape') + default +']\n')
	else:
		sys.stdout.write(msg + '[' + red + '\u2715'.encode("utf-8").decode('unicode_escape') + default +']\n')
def doinbackground(cmd, msg):
	threading.Thread(target=cmdtask, args=(cmd,)).start()
	progress(msg)

repo_url = ''

svn_username = 'zhouqing.qiu'
svn_password = 'zhouqing.qiu'

work_path = '/home/Disk_2TB/qiuzhouqing/MTK_RELEASE'
project_folder = 'MT6750'
alps_dir = work_path + '/' + project_folder
log_name = 'svn_log.txt'

tar_command = 'tar -xvzf '
cp_command = 'cp -rvf '
rm_command = 'rm -rvf '

svn_update_command = 'svn update --username ' + svn_username + ' --password ' + svn_password
svn_add_command = "svn st --no-ignore | awk '{if($1 == \"?\"){print $2}}' | xargs -r svn add"
svn_commit_command = 'svn commit --file '

patches = []

#SVN MESSAGE
svn_msg = '模块：patch\n修改点：%s\n%s'

#into project folder
#print(green)
#info('------------------------------ INTO FOLDER ----------------------------')
#print(alps_dir)
#result = commands.getstatusoutput('cd ' + alps_dir)
#if result[0]:
#	print(red + result[1] + default)
#	exit()
#update code
#info('------------------------------ UPDATE CODE ----------------------------')
os.chdir(alps_dir)
#doinbackground(svn_update_command, '#update    ')
info('------------------------------ PATCHES LIST----------------------------')
#print('------------------------------ PATCHES LIST----------------------------')
for f in os.listdir(work_path):
	if os.path.isfile(work_path + '/' + f) and f.endswith('tar.gz'):
		patches.append(f)
		#print(' ' * 4 + f)
		#info('-----------------------------------------------------------------------')
patches.sort()
for p in patches:
	print(' ' * 4 + p)
	#print('-----------------------------------------------------------------------')
	info('-----------------------------------------------------------------------')
in_msg = raw_input(highline + '\nAre you sure the patches\'s sequence is right, it is important (yes/no): ' + default)

while True:
	if 'no' == in_msg:
		info('Script will exit, thx for using!')
		exit()
	elif 'yes' != in_msg:
		error('Please input "yes" or "no"')
		in_msg = raw_input(highline+'\nplease check the patches\'s sequence!!!!(yes/no): '+default)
	else: 
		break

for patch in patches:
	info('\n-------- ' + patch[patch.rfind('_')+1 : patch.rfind(')') : 1] + ' --------')
	m_patch = patch
	m_patch = m_patch.replace('(', '\(')
	m_patch = m_patch.replace(')', '\)')
	print('#file operation')
	#begin unzip patch file
	os.chdir(work_path)
	doinbackground(tar_command + work_path + '/' + m_patch, '    --unzip     ')
	if result[0]:
		error(result[1])
		break
	#begin cover origin file)
	doinbackground(cp_command + work_path + '/alps/* ' + alps_dir, '    --copy      ')
	if result[0]:
		error(red + result[1])
		break
	#svn add
	print('#svn operation')
	os.chdir(alps_dir)
	#doinbackground(svn_add_command, '    --add       ')
	if result[0]:
		error(result[1])
		break
	#generate svn log
	patch_list = open(work_path + '/patch_list.txt','r')
	svn_log = open(work_path + '/' + log_name,'w+')
	commit_msg = svn_msg % (patch[0 : len(patch) - 7 : 1], patch_list.read())
	svn_log.write(commit_msg)
	patch_list.close()
	svn_log.close()
	#commit
	#doinbackground(svn_commit_command + work_path + '/svn_log.txt' , '    --commit    ')
	if result[0]:
		error(result[1])
		break
	#delete unzip files
	print('#finished')
	os.chdir(work_path)
	doinbackground(rm_command + 'alps/ patch_list.txt ' + log_name, '    --rm cache  ')

if 'yes' == raw_input(highline+'\nMTK Patch Finished, want to delete the patch tar? (yes/no): '+default):
	for patch in patches:
		os.remove(work_path + '/' + patch)

info('------------------------- THANK YOU FOR USING -----------------------')
