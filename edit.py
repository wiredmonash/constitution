#!/usr/bin/env python3

import argparse

def roman_to_int(roman, values={'M': 1000, 'D': 500, 'C': 100, 'L': 50,
								'X': 10, 'V': 5, 'I': 1}):
	#https://codereview.stackexchange.com/a/68301
	"""Convert from Roman numerals to an integer."""
	if 'I' == roman:
		return 1
	if 'V' == roman:
		return 5
	numbers = []
	for char in roman:
		numbers.append(values[char])
	total = 0
	for num1, num2 in zip(numbers, numbers[1:]):
		if num1 >= num2:
			total += num1
		else:
			total -= num1
	return total + num2


class MyParserFormatter(argparse.RawTextHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
	pass


def init_parser():
	parser = argparse.ArgumentParser(description='pdf/docx to md converter.',
									 formatter_class=MyParserFormatter)
	parser.add_argument('-i', action='store', type=argparse.FileType('r'), help='A file contatining the index (table of content) of file to be converted')
	parser.add_argument('-c', action='store', type=argparse.FileType('r'), help='A file contatining the main contents of file to be converted')
	parser.add_argument('-l', action='store', default='./logs.txt', help='File path to store the logs.')
	parser.add_argument('-o', action='store', default='./output.md', help='File path to store the converted results')
	return parser


def read(file):
	with open(file) as f:
		return f.read()


def process_content(content):
	logs = []
	content = content.splitlines()
	content = [i for i in content if i]

	for i in range(len(content)):
		line = content[i]
		try:
			if '(' == line[0]:
				index = line.index(')')
				n = line[1:index]
				if not n.isdigit():
					if ('i' in n) or ('i' == n) or ('v' == n):
						n = '\t\t{}'.format(roman_to_int(n.upper()))
					else:
						n = '\t{}'.format(ord(n)-96)
				sen = line[index+1:]
				content[i] = '{}. {}'.format(n, sen.strip())
			elif 'PART' == line[:4]:
				content[i] = '# {}'.format(line)
			elif 'Division' == line[:8]:
				content[i] = '## {}'.format(line)
			else:
				index = line.index(' ')
				try:
					n = int(line[:index])
					sen = line[index+1:]
				except:
					continue
				content[i] = '### {}. {}'.format(n, sen.strip())
		except Exception as e:
			logs.append('{}. {}'.format(i, line))
	return ('\n'.join(content), logs)


def process_toc(toc):
	logs = []
	toc = toc.splitlines()
	toc = [i for i in toc if i]
	try:
		for i in range(len(toc)):
			line = toc[i]
			if 'PART' == line[:4]:
				sen = line.split('\t')[0]
				sen = '[{}](#{})'.format(sen, sen.lower().replace(' ', '-'))
				toc[i] = sen
			elif 'DIVISION' == line[:8]:
				sen = line.split('\t')[0]
				sen = '[{}](#{})'.format(sen, sen.lower().replace(' ', '-'))
				toc[i] = '    - ' + sen
			else:
				n, sen, _ = line.split('\t')
				sen = '{}. {}'.format(n, sen)
				sen = '[{}](#{})'.format(sen, sen.lower().replace(' ', '-'))
				toc[i] = '        - ' + sen
	except Exception as e:
		logs.append('{}. {}'.format(i, line))

	return ('\n'.join(toc), logs)


def main():
	p = init_parser()
	args = p.parse_args()

	if not (args.i or args.c):
		p.error('da heck, gimme something to process')

	logs = []
	output = ''

	if args.i:
		(o, l) = process_toc(read(args.i.name))
		if l:
			logs += ['couldn\'t process these lines while processing table of contents'] + l
			
		header = '# Faculty of Information Technology Society\n\n![wired logo](./signature-logo.png)\n\n\nTable of contents\n=================\n\n'
		output += header + o

	if args.c:
		(o, l) = process_content(read(args.c.name))
		if l:
			logs += ['couldn\'t process these lines while processing the contents'] + l
		output += o

	with open(args.o, 'w') as f:
		f.write(output)

	if logs:
		with open(args.l, 'w') as f:
			f.write('\n'.join(logs))


if __name__ == '__main__':
	main()
