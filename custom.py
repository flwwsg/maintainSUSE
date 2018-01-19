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
import json
import pwd
from socket import timeout

# SUPPORTEDOS = ['opensuse', 'tumbleweed']
# path = os.path.abspath(__file__)
# fpath = os.path.join(os.path.dirname(path), 'configs.json')
# CONFIGS = json.load(open(fpath))

# def get_userinfo(uid=1000):
#     try:
#         infos = pwd.getpwuid(uid)
#     except Exception:
#         return None, None

#     dirname = infos.pw_dir
#     username = infos.pw_name
#     return username, dirname


# config = get_config()
# SOFTS = {'opensuse': ('basic_suse_softs', 'suse_softs')}


# def changerepo(plantform='opensuse', mirrorname='tuna'):
#     """change software repository to mirror site in china"""
#     mirrorurl = config['common'][mirrorname] + plantform
#     repos = config[plantform]['repos'].split()
#     reserved = config[plantform].get('reserved', '').split()
#     default_url = 'http://download.opensuse.org'
#     addrepo = 'sudo zypper addrepo --check --refresh --name "%s" %s "%s"'
#     removerepo = 'sudo zypper removerepo %s'

#     outs = os.popen('zypper repos -d').readlines()
#     newrepos = {}
#     for line in outs:
#         tmp = line.split('|')
#         if len(tmp) < 8 or tmp[1].strip() == 'Alias':
#             continue

#         alias = tmp[1].strip()
#         if alias not in reserved:
#             os.system(removerepo % alias)
#         else:
#             continue
#         if alias not in repos:
#             continue
#         url = tmp[8]
#         turl = url.replace(default_url, mirrorurl)
#         tname = alias if alias.startswith(
#             mirrorname + '-') else mirrorname + '-' + alias
#         newrepos[tname] = turl

#     for name, url in newrepos.items():
#         os.system(addrepo % (name, url, name))
#     os.system('sudo  zypper update ')


# def install_software(plantform='opensuse', softs=[]):
#     if not softs:
#         tlist = SOFTS.get(plantform, [])
#         for ll in tlist:
#             softs.extend(config['common'].get(ll, []).split(',')[:-1])
#     for soft in softs:
#         os.system('sudo zypper in -y %s' % soft.strip())


# def install_pip_module(file='', softs=[]):
#     pipindex = config['common'].get(
#         'pipindex', 'https://pypi.python.org/simple').strip()
#     if not softs:
#         softs = config['common'].get('pip_softs', []).split(',')[:-1]
        
#     if not file:
#         os.system(
#             'sudo pip install -r requirements.txt -i %s' % pipindex)
#     else:
#         os.system(
#             'sudo pip install -r %s -i %s' % (file, pipindex))

#     for soft in softs:
#         os.system(
#             'sudo pip install -i %s %s' % (pipindex, soft))


# def improved_bash(alias={}, echos=[], cmds=[], filename=''):
#     username, userdir = get_userinfo()
#     if not filename:
#         filename = userdir+'/.bashrc'

#     if not alias:
#         newalias = config['bash']['alias'].split(',')[:-1]
#         for tmp in newalias:
#             tmp = tmp.strip()
#             func = tmp.strip().split('=')[0]
#             alias[func] = tmp[len(func)+1:]

#     if not echos:
#         echos = config['bash']['echos'].split(',')[:-1]

#     if not cmds:
#         cmds = config['bash']['cmds'].split(',')[:-1]
        
#     for cmd, alia in alias.items():
#         os.system('echo "alias %s=%s" >> %s' % (cmd, alia, filename))

#     for cmd in echos:
#         os.system('echo \'%s >> %s\'' % (cmd.strip(), filename))

#     for cmd in cmds:
#         os.system(cmd)


# def add_repos(repos='', plantform='opensuse', version='42.2'):
#     if config[plantform]['version'] != version:
#         return False
#     if not repos:
#         repos = config[plantform]['addrepos'].split(',')[:-1]
#     for repo in repos:
#         os.system('sudo zypper ar -fc %s' % repo.strip())
#     repos = config['common']['cusrepos'].split(',')[:-1]
#     for repo in repos:
#         # print(repo.lstrip())
#         os.system(repo.lstrip())
#     os.system('sudo zypper  --gpg-auto-import-keys ref')
#     return True


# def add_group():
#     groups = config['common']['group'].split(',')[:-1]
#     username, userdir = get_userinfo()
#     for g in groups:
#         os.system(g.strip() % username)

class CustomOS(object):
    """change repository to chinese mirror"""

    def __init__(self, mirror_name, file_name='configs.json'):
        self.mirror_name = mirror_name
        self.config_file = file_name
        self.plantform = ''
        self.version = ''
        
    def check_prerequirements(self):
        '''
        check requirement to run this program
        '''
        self._chk_permission()
        self._get_config()
        self._get_plantform()
        self._chk_config()

    def _get_plantform(self):
        with open('/etc/os-release') as f:
            infos = f.readlines()
        for line in infos:
            tmp = line.strip().split('=')
            name = tmp[0]
            if name == 'ID':
                self.plantform = tmp[1].replace('"','')
            elif name == 'VERSION':
                self.version = tmp[1].replace('"', '')
        if not self.plantform or not self.version:
            raise Exception('Unknown os.')

    def _chk_permission(self):
        euid = os.geteuid()
        if euid != 0:
            print('try: sudo python3 custom.py')
            exit(1)

    def _get_config(self):
        try:
            self.configs = json.load(open(self.config_file))
        except Exception:
            print('Can not read json file named %s, properly wrong json formate' % self.config_file)
            sys.exit(1)

    def _chk_config(self):
        '''
        checking parameters specified in configs
        '''

        # checking repository
        if self.plantform not in self.configs:
            raise Exception('Not supported os named %s' % self.plantform)
        if self.version not in self.configs[self.plantform]['os']:
            raise Exception('Not supported version %s of %s' % (self.version, self.plantform))
        for repo in self.configs[self.plantform]['os'][self.version]['repos']:
            url = repo['url']
            self.chk_url(url)

        if not all([k in self.configs for k in ['common', 'bash']]):
            raise Exception('Can not find common or bash parameters in file named %s' % self.config_file)

        common_item = ['pypi', 'host', 'pip_software', self.mirror_name]
        if not all([k in self.configs['common'] for k in ['pypi', 'host', 'pip_software', self.mirror_name]]):
            raise Exception('Can not find all "%s" in common in file named %s' % (common_item, self.config_file))

        # checking common
        if 'pypi' not in self.configs['common']:
            raise Exception('Can not find pypi item in common dictory') 
        for url in self.configs['common']['pypi']:
            self.chk_url(url)
        mirror_url = self.configs['common'][self.mirror_name]
        self.chk_url(mirror_url)
        host_url = self.configs['common']['host']
        self.chk_url(host_url)

    @staticmethod
    def chk_url(url, time_out=30):
        try:
            resp = urlopen(url, timeout=time_out).read()
        except timeout:
            raise Exception('Can not access %s' % url)   

    def add_repo(self):
        '''
        add repository
        '''
        repos = self.configs[self.plantform]['os'][self.version]['repos']
        custom_repos = self.configs[self.plantform]['custom_repos']
        addrepo = 'sudo zypper addrepo --check --refresh --name "%s" %s "%s"'
        for repo in repos:
            os.system(addrepo % (repo['name'], repo['url'], repo['name']))
        for crepo in custom_repos:
            os.system(crepo)

    def get_hosts(self):
        '''
        get host file to fight GFW
        '''
        html = urlopen(self.configs['common']['host'], timeout=20)
        with open('hosts', 'wb') as f:
            f.write(html.read())
        # copy hosts
        os.system('sudo cat ./hosts >> /etc/hosts')
        os.system('sudo systemctl restart NetworkManager')
        time.sleep(10)

    def install_software(self):
        '''
        install software
        '''



# # #configure git
# # os.system('git config --global user.email "2319406132@qq.com"')
# # os.system("git config --global user.name 'flwwsg'")

# # # add groups
# # for group in groups:
# # 	os.system('sudo usermod -aG %s lblue' % group)
# # 	os.system('sudo usermod -aG %s dev' % group)
# # # sudo usermod -aG groupName userName
# # # sudo usermod -aG vboxusers lblue

# if __name__ == '__main__':
#     def testing():
#         print('ok')

#     flist = [
#         changerepo,
#         install_software,
#         get_hosts,
#         install_pip_module,
#         improved_bash,
#         add_repos,
#         add_group,
#         testing,
#     ]
#     if len(sys.argv) < 2:
#         print('using python3 changeRepo.py function_you_want_to_run')
#         for i, func in enumerate(flist):
#             print('for %s enter: %s\n' % (func.__name__, i + 1))
#     else:
#         for num in sys.argv:
#             try:
#             # print(sys.argv)
#             	flist[int(num) - 1]()
#             except Exception:
#                 pass
