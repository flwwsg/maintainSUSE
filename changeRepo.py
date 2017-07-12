#!/usr/bin/python3
"""
Changing Repository from dowload.opensuse.org to mirrors.tuna.tsinghua.edu.cn/opensuse and 
install popular software.
Running only once on first running after system installed
"""
import os
import sys
import time
import configparser
from urllib.request import urlopen
import pwd

SUPPORTEDOS = ['opensuse', 'tumbleweed']


def get_config(file='configs'):
    config = configparser.ConfigParser()
    config.read_file(open(file))
    return config


config = get_config()


def changerepo(plantform='opensuse', mirrorname='tuna'):
    """change software repository to mirror site in china"""
    mirrorurl = config['common'][mirrorname] + plantform
    repos = config[plantform]['repos'].split()
    reserved = config[plantform].get('reserved', '').split()
    default_url = 'http://download.opensuse.org'
    addrepo = 'sudo zypper addrepo --check --refresh --name "%s" %s "%s"'
    removerepo = 'sudo zypper removerepo %s'

    outs = os.popen('zypper repos -d').readlines()
    newrepos = {}
    for line in outs:
        tmp = line.split('|')
        if len(tmp) < 8 or tmp[1].strip() == 'Alias':
            continue

        alias = tmp[1].strip()
        if alias not in reserved:
            os.system(removerepo % alias)
        if alias not in repos:
            continue
        url = tmp[8]
        turl = url.replace(default_url, mirrorurl)
        tname = alias if alias.startswith(
            mirrorname + '-') else mirrorname + '-' + alias
        newrepos[tname] = turl

    for name, url in newrepos.items():
        os.system(addrepo % (name, url, name))


def install_software(plantform='opensuse', softs=[]):
    for soft in softs:
        os.system('sudo zypper in -y %s' % soft)


def install_pip_module(file='', softs=[]):
    pipindex = config['common'].get(
        'pipindex', 'https://pypi.python.org/simple')
    if not file:
        os.system(
            'sudo pip install -r requirements.txt -i %s' % pipindex)
    else:
        os.system(
            'sudo pip install -r %s -i %s' % (file, pipindex))

    if softs:
        for soft in softs:
            os.system(
                'sudo pip install -i %s %s' % (pipindex, soft))
    else:
        pass


def improved_bash(alias={}, echos=[], cmds=[], filename=''):
    if not filename:
        filename = '~/.bashrc'

    for cmd, alia in alias.items():
        os.system('echo "alias %s=\'%s\'" >> %s' % (cmd, alia, filename))

    for cmd in echos:
        os.system('echo %s >> %s' % (cmd, filename))

    for cmd in cmds:
        os.system(cmd)


def add_repos(repos='', plantform='opensuse', version='42.2'):
    if config[plantform]['version'] != version:
        return False
    if not repos:
        repos = config[plantform]['addrepos'].split(',')[:-1]
    for repo in repos:
        os.system('sudo zypper ar -fc %s' % repo.strip())
    repos = config['common']['cusrepos'].split(',')[:-1]
    for repo in repos:
        # print(repo.lstrip())
        os.system(repo.lstrip())
    return True


def get_hosts():
    html = urlopen(
        'https://coding.net/u/scaffrey/p/hosts/git/raw/master/hosts')
    with open('hosts', 'wb') as f:
        f.write(html.read())
    # copy hosts
    os.system('sudo cat ./hosts >> /etc/hosts')
    os.system('sudo systemctl restart NetworkManager')
    time.sleep(10)


def get_userinfo(uid=1000):
    try:
        infos = pwd.getpwuid(uid)
    except Exception:
        return None

    dirname = infos.pw_dir
    username = infos.pw_name
    return username, dirname


class ChangeRepo(object):
    """change repository to chinese mirror"""

    def __init__(self, plantform='', version='', config='configs'):
        self._chk_permission()
        self.plantform = plantform
        self.version = version
        if not self.plantform or not self.version:
            self._get_plantform()

    def _get_plantform(self):
        versions = os.popen('cat /etc/os-release').readlines()
        infos = {'ID': 'plantform', 'VERSION': 'version'}
        for line in versions:
            tmp = line.strip().replace('"', '').split('=')
            if tmp[0] in infos.keys():
                setattr(self, infos[tmp[0]], tmp[1])

    def _chk_permission(self):
        euid = os.geteuid()
        if euid != 0:
            print('try: sudo python3 changeRepo.py')
            exit(1)


# #configure git
# os.system('git config --global user.email "2319406132@qq.com"')
# os.system("git config --global user.name 'flwwsg'")

# # add groups
# for group in groups:
# 	os.system('sudo usermod -aG %s lblue' % group)
# 	os.system('sudo usermod -aG %s dev' % group)
# # sudo usermod -aG groupName userName
# # sudo usermod -aG vboxusers lblue

if __name__ == '__main__':
    def testing():
        print('ok')

    flist = [
        changerepo,
        install_software,
        get_hosts,
        install_pip_module,
        improved_bash,
        add_repos,
        testing,
    ]
    if len(sys.argv) < 2:
        print('using python3 changeRepo.py function_you_want_to_run')
        for i, func in enumerate(flist):
            print('for %s enter: %s\n' % (func.__name__, i+1))
    else:
        for num in sys.argv:
            try:
                flist[int(num)-1]()
            except Exception:
                print('something wrong')
    
