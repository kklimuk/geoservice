from sys import stdin, argv
import json

# hook this up as a unix utility:
# reads from STDIN and writes to STDOUT
if __name__ == '__main__':
	with stdin as standard_input:
		data = json.loads(stdin.read())['features']
		for index, i in enumerate(xrange(0, len(data), 2000)):
			with file(argv[1] + str(index) +  '.json', 'w+') as current:
				current.write(json.dumps(data[i:i+2000]))