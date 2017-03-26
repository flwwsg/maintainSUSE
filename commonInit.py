"""
common file for maintaining opensuse
"""
import os


USER = os.getlogin() 
HOME = '/home/%s' % USER

#Changing file mod to 775 for sharing .
#replace space (' ') in path to ('\ ') avoid misstake in bash
def changeMod(mod=775, directories=None):
	chmod = 'sudo chmod -R %s %s'
	if not directories:
		directories = ['dev', 'django18', 'bin', 'VirtualBox VMs','Documents', 'Downloads']
	for folder in directories:
		path = os.path.join(HOME, folder)
		if os.path.exists(path):
			path = path.replace(' ','\ ')
			cmd = chmod % (mod, path)
			os.system(cmd)
			# print(cmd)
