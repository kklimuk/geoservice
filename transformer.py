from sys import stdin
import json

# hook this up as a unix utility:
# reads from STDIN and writes to STDOUT
if __name__ == '__main__':
	with stdin as standard_input:
		print json.dumps(json.loads(stdin.read())['features'])