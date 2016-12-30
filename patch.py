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
def compare(x, y):
    newx = x[x.rfind('P', 0, len(x)) + 1:x.rfind(')', 0, len(x))]
    newy = y[y.rfind('P', 0, len(y)) + 1:y.rfind(')', 0, len(y))]
    if newx < newy:
        return -1
    elif newx > newy:
        return 1
    else: 
        return 0

class CommandThread (threading.Thread):
    def __init__(self, command):
        threading.Thread.__init__(self)
	self.command = command
        self.running = True
    def run(self):
        self.result = commands.getstatusoutput(self.command)
        self.running = False

def show_progress(message, thread):
    t = 0
    while thread.running:
        sys.stdout.write(message + '[/]') if t % 2 == 0 else sys.stdout.write(message + '[\]')
        sys.stdout.write('\r')
        sys.stdout.flush()
        t += 1
        time.sleep(1)
    if thread.result[0] == 0:
        sys.stdout.write(message + '[' + green + '✔' + default + ']\n')
    else:
        sys.stdout.write(message + '[' + red + '✕' + default + ']\n')
        error(thread.result[1])
	exit()

def do_in_background(thread, message):
    thread.start()
    show_progress(message, thread)

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
svn_delete = "svn delete"
svn_commit_command = 'svn commit --file '

#SVN MESSAGE
svn_msg = '模块：patch\n修改点：%s\n%s'

print(green + '----------------------- MTK AUTO PATCH SCRIPT -----------------------' + default)

# SVN project
alps_dir = ''
svn_projects = []
dirs = [dir for dir in os.listdir(work_path) if os.path.isdir(work_path + '/' + dir)]
for dir in dirs:
    files = os.listdir(work_path + '/' + dir)
    if len(files) > 2:
	for file in files:
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
do_in_background(CommandThread(svn_update_command), '    --update    ')
patches = [f for f in os.listdir(work_path) if os.path.isfile(work_path + '/' + f) and f.endswith('tar.gz')]
patches.sort(compare)
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
    do_in_background(CommandThread(tar_command + work_path + '/' + m_patch), '    --unzip     ')
    #begin cover origin file)
    do_in_background(CommandThread(cp_command + work_path + '/alps/* ' + alps_dir), '    --copy      ')
    #svn add
    info('#svn operation')
    os.chdir(alps_dir)
    do_in_background(CommandThread(svn_add_command), '    --add       ')
    #generate svn log
    patch_list = open(work_path + '/patch_list.txt','r')
    svn_log = open(work_path + '/' + log_name,'w+')
    commit_msg = svn_msg % (patch[0 : len(patch) - 7 : 1], patch_list.read())
    svn_log.write(commit_msg)
    patch_list.close()
    svn_log.close()
    #svn delete
    patch_list = open(work_path + '/patch_list.txt','r')
    delete_list = ''
    for line in patch_list:
        if line.startswith('delete '):
            delete_list += line[6 : len(line) - 1]
    patch_list.close()
    if delete_list != '':
        do_in_background(CommandThread(svn_delete + delete_list + '&& rm -rf' + delete_list), '    --delete    ')
    #commit
    do_in_background(CommandThread(svn_commit_command + work_path + '/' + log_name), '    --commit    ')
    #delete unzip files
    info('#finished')
    os.chdir(work_path)
    do_in_background(CommandThread(rm_command + 'alps/ patch_list.txt ' + log_name), '    --rm cache  ')

if 'yes' == raw_input(yellow+'MTK Patch Finished, want to delete the patch tar? (yes/no): '+default):
    for patch in patches:
        os.remove(work_path + '/' + patch)

print(green + '------------------------ THANK YOU FOR USING ------------------------' + default)
