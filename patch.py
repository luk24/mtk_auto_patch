#! /usr/bin/python
#-*-coding:utf-8-*-
import os
import commands
import sys,time
import subprocess
import threading

SCRIPT_VERSION = '0.1'

#text color
highline = '\033[1m'
green = '\033[1;32m'
red = '\033[1;31m'
yellow = '\033[0;33m'
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
		sys.stdout.write(msg + '[' + green + '✔' + default +']\n')
	else:
		sys.stdout.write(msg + '[' + red + '✕' + default +']\n')

def doinbackground(cmd, msg):
	threading.Thread(target=cmdtask, args=(cmd,)).start()
	progress(msg)

repo_url = ''

svn_username = ''
svn_password = ''

work_path = os.getcwd()
alps_dir = ''
log_name = 'svn_log.txt'

tar_command = 'tar -xvzf '
cp_command = 'cp -rvf '
rm_command = 'rm -rvf '
svn_update_command = 'svn update'
svn_add_command = "svn st --no-ignore | awk '{if($1 == \"?\"){print $2}}' | xargs -r svn add"
svn_commit_command = 'svn commit --file '

#SVN MESSAGE
svn_msg = '模块：patch\n修改点：%s\n%s'

print(green + '--------------------- MTK AUTO PATCH SCRIPT -------------------------' + default)

# SVN project
alps_dir = ''
svn_projects = []
dirs = [dir for dir in os.listdir(work_path) if os.path.isdir(work_path + '/' + dir)]
for dir in dirs:
    for file in os.listdir(work_path + '/' + dir):
        if file == '.svn':
            svn_projects.append(dir)
if len(svn_projects) > 0:
    info('#found dirs')
    number = 0
    for project in svn_projects:
        number += 1
        print('    ' + str(number) + '. ' + work_path + '/' + project);
    u_in = input(yellow + 'Please choose a dir as your svn project(choose \'0\' to input path): ' + default)
    if u_in > 0:
        alps_dir = work_path + '/' + svn_projects[u_in-1]
    else:
        alps_dir = raw_input('Please input svn project path: ')
else:
    alps_dir = aw_input(yellow + 'Not found svn project, Please input path: ' + default)

# show svn config
svn_config_path = os.environ['HOME'] + '/' + '.subversion/auth/svn.simple'
files = os.listdir(svn_config_path)
if len(files) == 1 and os.path.isfile(svn_config_path + '/' + files[0]):
    svn_config_path += '/' + files[0]
    svn_config = open(svn_config_path, 'r')
    svn_line = 0
    svn_username_line = 0
    svn_password_line = 0
    for line in svn_config.readlines():
        svn_line += 1
        if svn_line == svn_username_line:
            svn_username = line[:len(line) -1:]
        elif svn_line == svn_password_line:
            svn_password = line[:len(line) -1:]
        if line.find('username') != -1:
            svn_username_line = 2 + svn_line
        elif line.find('password') != -1:
            svn_password_line = 2 + svn_line
    svn_config.close()
info('#svn config')
print('    --username: ' + svn_username)
print('    --password: ' + svn_password)
if raw_input(yellow + 'Do you want to change the svn account?(yes/no): ' + default) == 'yes':
    svn_username = raw_input('svn username: ')
    svn_password = raw_input('svn_password: ')
    svn_update_command = 'svn update --username ' + svn_username + ' --password ' + svn_password

#update code
info('#update code')
os.chdir(alps_dir)
doinbackground(svn_update_command, '    --update    ')
patches = [f for f in os.listdir(work_path) if os.path.isfile(work_path + '/' + f) and f.endswith('tar.gz')]
patches.sort()
if len(patches) > 0:
	info('#patch list')
	for p in patches:
		print('    ' + p)
	if 'yes' != raw_input(yellow + 'Are you sure the patches\'s sequence is right, it is important (yes/no): ' + default):
		exit()
else:
	error('Not found patches files, execute over!')
	exit()

for patch in patches:
	info('-------- ' + patch[patch.rfind('_')+1 : patch.rfind(')') : 1] + ' --------')
	m_patch = patch
	m_patch = m_patch.replace('(', '\(')
	m_patch = m_patch.replace(')', '\)')
	info('#file operation')
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
	info('#svn operation')
	os.chdir(alps_dir)
	doinbackground(svn_add_command, '    --add       ')
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
	doinbackground(svn_commit_command + work_path + '/' + log_name , '    --commit    ')
	if result[0]:
		error(result[1])
		break
	#delete unzip files
	info('#finished')
	os.chdir(work_path)
	doinbackground(rm_command + 'alps/ patch_list.txt ' + log_name, '    --rm cache  ')

if 'yes' == raw_input(yellow+'MTK Patch Finished, want to delete the patch tar? (yes/no): '+default):
	for patch in patches:
		os.remove(work_path + '/' + patch)

print(green+'------------------------- THANK YOU FOR USING -----------------------'+default)
