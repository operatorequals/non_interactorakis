#!/usr/bin/env python


import sys
import os
import pty

def execTTY() :
	import tty
#	print "Getting TTY..."
	fileno = sys.stdin.fileno()
#	tty.setraw(fileno)
#	tty.setcbreak(fileno)
	pty.spawn(["./%s" % sys.argv[0], sys.argv[1]])	# respawns the process in TTY
	sys.exit(0)


def boolify(s):
    if s == 'True':
        return True
    if s == 'False':
        return False
    raise ValueError("huh?")

def autoconvert(s):
    for fn in (boolify, int, float):
        try:
            return fn(s)
        except ValueError:
            pass
    return s


try :
	filename = sys.argv[1]
	file = open(filename, 'r+')

	if not sys.stdin.isatty() : execTTY()	# checks if it executes in a TTY
						# if not it spawns one and forks to it
except Exception as e:
#	print e
	print "Usage:"
	print "	%s file_to_edit" % sys.argv[0]
	sys.exit(1)


print "==== File to edit '%s' ====" % filename
print "Use 'quit' (NOT 'exit') to exit the editor..."
lines = file.readlines()


Less_step = 10
counter = 0
def lessFile(less_step = Less_step) :

#	if less_step != Less_step :
	global Less_step
	Less_step = less_step

	global counter
	if counter + less_step > len(lines) :
		less_step = len(lines) - counter

	displayFile(counter, counter+less_step)
	counter += less_step
	if counter >= len(lines) :
		counter = 0


def displayFile(start = 0, stop = None, lines_ = None) :
	if lines_ == None :
		lines_ = lines
	if stop == None :
		stop = len(lines_)
	if stop > len(lines) :
		stop = len(lines_)
	for number in range(start,stop) :
		print "{0:4} ~ {1}" .format (number, lines_[number]),
	print


def editLine(line_n) :
	print "	Editing the following line:"
	line = lines[line_n]
	print "=" * len(line)
	print lines[line_n],
	print "=" * len(line)

	new_line = raw_input("Editing Line> ")
	lines[line_n] = new_line + os.linesep


def showHelp() :
	print "=" * 20
	for comm in commands.keys() :
		print "{0}\t- {1}\n".format(comm, commands[comm][1])
	print "=" * 20


def saveFile() :
	toSave = ''.join( lines )
	nlines = len(lines)
	global file			# close the reading descriptor
	file.close()
	file = open(filename, 'w')	# purge content
	file.write(toSave)		# write whole new content
	file.close()

	file = open(filename, 'r')	# reopen for reading
	print "Saved %d lines!" % nlines


def clearFile() :
	global lines
	lines = []
	print "The file is empty!"


def exitEditor() :
	file.close()
	sys.exit(0)


def overwriteFile() :
	rand_str = os.urandom(8).encode('hex')
	print "You are about to overwrite the whole file."
	print "Type '%s' to return to Editor Prompt" % rand_str
	option = raw_input("Are you sure? [y/N]")
	if not (option.lower() == 'y' or option.lower() == 'yes') :
		print "Aborted"
		return

	global lines
	lines = []
	i = 0
	line = ''
	while line.rstrip() != rand_str :
		line = raw_input( "{:4}> ".format(i) )
		lines.append( line + os.linesep )
		i += 1
	lines = lines[:-1]	# remove the hash added at the end
	print "Wrote %d lines to the file!" % (len(lines))

def swapLines(l1, l2) :
	lines[l1], lines[l2] = lines[l2], lines[l1]


def searchLines(keyword) :
	ans = []
	for line in lines :
		if keyword in line :
			ans.append( line )
	displayFile(lines_ = ans)

import re
def searchRegex(regex) :
	ans = []
	for line in lines :
		match = re.search(regex, line)
		if match :
			ans.append( line )
	displayFile(lines_ = ans)


commands = {
"display" : (displayFile, "Displays the whole or a portion of the file.\nExample: display [starting_line], [ending_line]"), 
"edit" : (editLine, "Edit a specific line.\nExample: edit <line_to_edit>"),
"save" : (saveFile, "Save file changes.\nExample: save"),
"quit" : (exitEditor, "Exits the Editor"),
"help" : (showHelp, "Shows list of commands and examples"),
"less" : (lessFile, "A 'less' like way to view the file. Uses an optional 'step' argument"),
"clear" : (clearFile, "Clears the whole file (doesn't automatically save)" ),
"overwrite" : (overwriteFile, "Lets you write the whole file from scratch using line-by-line editing"),
"swap" : (swapLines, "Swaps 2 lines by line number given as arguments"),
"search" : (searchLines, "Searches all lines for a keyword given as argument"),
"regex" : (searchRegex, "Searces all lines for regex given as argument")

}


while True :
	comm = raw_input("Editor> ")
	if not comm :
		continue

	tokens = comm.split()
	comm = tokens[0]

	args = [ autoconvert(tok) for tok in tokens[1:] ]
	if comm.lower() in commands.keys() :
		try :
			commands[comm][0](*args)
		except :
			print "Command '%s' needs more parameters. Check 'help'." % comm

	else :
		print "Command '%s' not found." % comm
		print "Type 'help' for a list of commands"


#	if comm == 'help' :
#		showHelp()
