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

	if not sys.stdin.isatty() : execTTY()

except Exception as e:
#	print e
	print "Usage:"
	print "	%s file_to_edit" % sys.argv[0]
	sys.exit(1)


print "==== File to edit '%s' ====" % filename
print "Use 'quit' (NOT 'exit') to exit the editor..."
lines = file.readlines()

less_step = 10
counter = 0
def lessFile(less_step = less_step) :

	global counter
	if counter + less_step > len(lines) :
		less_step = len(lines) - counter

	displayFile(counter, counter+less_step)
	counter += less_step
	if counter >= len(lines) :
		counter = 0


def displayFile(start = 0, stop = None) :
	if stop == None :
		stop = len(lines)
	if stop > len(lines) :
		stop = len(lines)
	for number in range(start,stop) :
		print "{0:4} ~ {1}" .format (number, lines[number]),


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


def exitEditor() :
	file.close()
#	raise Exception("Exiting...")
	sys.exit(0)


commands = {
"display" : (displayFile, "Displays the whole or a portion of the file.\nExample: display [starting_line], [ending_line]"), 
"edit" : (editLine, "Edit a specific line.\nExample: edit <line_to_edit>"),
"save" : (saveFile, "Save file changes.\nExample: save"),
"quit" : (exitEditor, "Exits the Editor"),
"help" : (showHelp, "Shows list of commands and examples"),
"less" : (lessFile, "A 'less' like way to view the file")
}


while True :
	comm = raw_input("Editor> ")
	if not comm :
		continue

	tokens = comm.split()
	comm = tokens[0]

	args = [ autoconvert(tok) for tok in tokens[1:] ]
	if tokens[0].lower() in commands.keys() :
		commands[comm][0](*args)

	else :
		print "Command '%s' not found." % comm
		print "Type 'help' for a list of commands"


#	if comm == 'help' :
#		showHelp()
