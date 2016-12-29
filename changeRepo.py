#!/usr/bin/python3
import os, sys

euid = os.geteuid()
if euid != 0:
	print('try: sudo python3 changeRepo.py')
	exit(1)

pattern = 'http://download.opensuse.org'
replace = 'https://mirrors.tuna.tsinghua.edu.cn/opensuse'
softwares = ['git', 'fcitx-table-cn-wubi-pinyin', 'chromium']
ignore = ['repo-debug', 'repo-debug-non-oss', 'repo-debug-update',
			'repo-debug-update-non-oss','repo-source', 'repo-source-non-oss']
reserve = ['repo-update','repo-update-non-oss']
addrepo = 'sudo zypper addrepo --check --refresh --name "%s" %s "%s"'
remove = 'sudo zypper removerepo %s'
packman = 'https://mirrors.tuna.tsinghua.edu.cn/packman/suse/%s/'

#packman
versions = os.popen('cat /etc/os-release').readlines()
for line in versions:
	tmp = line.strip().replace('"','').split('=')
	if tmp[0] == 'PRETTY_NAME':
		version = tmp[1].replace(' ','_')
		break
repos = dict()
repos['tuna-packman'] = packman % version

outs = os.popen('zypper repos -d').readlines()
for line in outs[2:]:
	tmp = line.split('|')
	alias = tmp[1].strip()
	url = tmp[8]
	os.system(remove % alias)
	if alias in ignore:
		continue
	else:
		if alias in reserve:
			repos[alias] = url
		turl = url.replace(pattern, replace)
		tname = alias if alias.startswith('tuna-') else 'tuna-'+alias
		repos[tname] = turl	

for name, url in repos.items():
	os.system(addrepo % (name, url, name))

#copy hosts
os.system('sudo cp ./hosts /etc/')
os.system('sudo systemctl restart NetworkManager')
# zypper refresh
os.system('sudo zypper refresh')

for software in softwares:
	os.system('sudo zypper in -y %s' % s software)
