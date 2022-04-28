#!/usr/bin/env python3
import os
import re
import shutil
import sys


if __name__ == '__main__':
	old_name = open('Makefile').readline().split('=')[1].strip()
	if not os.path.exists(old_name):
		print(f'There is no dir with name {old_name}, please rename it manually')

	filenames = [
		'README.md',
		'setup.py',
		'run.py',
		'Makefile',
	]

	new_name = input('Enter new project name: ').replace('-', '_')

	if re.match(r'\d+.*', new_name):
		print('Python package name can not starts with digit!')
		sys.exit(-1)

	if not new_name:
		print('Invalid name!')
		sys.exit(-1)

	shutil.move(old_name, new_name)

	for f in filenames:
		content = open(f).read()
		new_content = content.replace(old_name, new_name)
		open(f, 'w').write(new_content)

	print('Project was successfully renamed')
