import glob

import sys
import os

if len(sys.argv) < 2:
	print (f'USAGE: {sys.argv[0]} <path to directory>')
	exit(1)

dir_path = sys.argv[1]

if not os.path.exists(dir_path):
	print('{dir_path} not found')
	exit(1)

if not os.path.isdir(dir_path):
	print('{dir_path} is not a directory')
	exit(1)

filenames = glob.glob(f'{dir_path}/*.txt')

if not os.path.exists(f'{dir_path}/no_accents'):
	os.mkdir(f'{dir_path}/no_accents')

accent = '́'
for filename in filenames:
	short_f = os.path.basename(os.path.normpath(filename))
	with open(f'{filename}', 'r') as f:
		raw_text = f.read()
	with open(f'{dir_path}/no_accents/{short_f}', 'w') as f:
		print(raw_text.replace(accent, ''), file=f)

