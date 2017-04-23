"""
common file for maintaining opensuse
"""
import os


USER = os.getlogin() 
HOME = '/home/%s' % USER

# folder listed in dirfilters will be unchanged
dirfilters = {'dev':['lims'], 'Downloads':['dev']}

#Changing file mod to 775 for sharing .
#replace space (' ') in path to ('\ ') avoid misstake in bash
def changeMod(mod=775, directories=None):
	chmod = 'sudo chmod -R %s %s'
	if not directories:
		directories = ['dev', 'django18', 'bin', 'VirtualBox VMs','Documents', 'Downloads', 'Music']
	for folder in directories:
		path = os.path.join(HOME, folder)
		if not os.path.exists(path):
			continue

		if folder in dirfilters.keys():
			subdirs = os.listdir(path)
			remain = set(subdirs) - set(dirfilters[folder])
			remain = list(remain)
			# print(remain)
			for ipath in remain:
				newpath = os.path.join(path, ipath)
				# print(newpath)
				if not os.path.exists(newpath):
					continue
				newpath = escapath(newpath)
				cmd = chmod % (mod, newpath)
				os.system(cmd)
				# print(cmd)
		else:	
			path = escapath(path)
			cmd = chmod % (mod, path)
			os.system(cmd)
			# print(cmd)

def escapath(path):
	toescap = ['(',')',"'",'"', ' ']
	for ch in toescap:
		if ch in path:
			path = path.replace(ch,'\\'+ch)
	return path

if __name__ == '__main__':
	changeMod()
