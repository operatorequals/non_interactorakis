#!/usr/bin/env python

import sys
import os
import pty
import re


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
	file = open(filename, 'r')

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
	global counter
	if less_step == 0 :
		counter = 0
		less_step = Less_step

	Less_step = less_step

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
	global Buffers
	lines, filename, file = Buffers[ cur_buffer ]
	if file == None :
		filename = raw_input("Select filename/filepath to Save: ")
	else :
		file.close()			# close the reading descriptor

	toSave = ''.join( lines )
	nlines = len( lines )
	try :
		file = open(filename, 'w')	# purge content
	except :
		print "Cannot write to '%s'. Didn't save." % filename
		return

	file.write(toSave)			# write whole new content
	file.close()

	file = open(filename, 'r')	# reopen for reading ONLY
	Buffers[ cur_buffer ] = (lines, filename, file)
	print "Saved %d lines!" % nlines


def clearFile() :
	global lines
	lines = []
	print "The file is empty!"


def exitEditor() :
	global file
	file.close()
	sys.exit(0)


def overwriteFile() :
	rand_str = os.urandom(8).encode('hex')
	print "You are about to overwrite the whole file."
	option = raw_input("Are you sure? [y/N]")
	if not (option.lower() == 'y' or option.lower() == 'yes') :
		print "Aborted"
		return

	global lines
	lines = perLineWrite()
	print "Wrote %d lines! Changes HAVEN'T been saved" % (len(lines))


def perLineWrite() :

	rand_str = os.urandom(8).encode('hex')
	print "Type '%s' to return to Editor Prompt" % rand_str

        buffer = []
        i = 0
        line = ''
        while line.rstrip() != rand_str :
                line = raw_input( "{:4}> ".format(i) )
                buffer.append( line + os.linesep )
                i += 1
        buffer = buffer[:-1]      # remove the hash added at the end

	return buffer


def insertLine( line_n = None ) :
	global lines
	if line_n == None :
		line_n = len(lines)
	print "Type the line to insert at line number %d" % line_n
	line = raw_input("!> ")
	lines.insert( line_n, line + os.linesep )


def deleteLine( line_n ) :
	global lines
	lines.pop(line_n)


def swapLines(l1, l2) :
	lines[l1], lines[l2] = lines[l2], lines[l1]


def searchLines(keyword) :
	ans = []
	for line in lines :
		if keyword in line :
			ans.append( line )
	displayFile(lines_ = ans)


def searchRegex(regex) :
	ans = []
	for line in lines :
		match = re.search(regex, line)
		if match :
			ans.append( line )
	displayFile(lines_ = ans)


Buffers = {'MAIN' : (lines, filename, file)}
cur_buffer = 'MAIN'
def bufferSelect ( buffer_ = None ) :

	if buffer_ == None :
		print "Buffers:"

		for br in Buffers.keys() :
			print " ~ %s" % br
		return

	Buffers[ buffer_ ] = ([], None, None)
	global cur_buffer
	cur_buffer = buffer_
	global lines
	global filename
	global file
	lines, filename, file = Buffers[ buffer_ ] 
	print "Created new Buffer '%s'" % buffer_


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
"regex" : (searchRegex, "Searces all lines for regex given as argument"),
"insert" : (insertLine, "Type the line to insert at the line number specified as argument (default appends the line to the file)"),
"delete" : (deleteLine, "Deletes the line at the line number specified as argument" ),

"buffer" : (bufferSelect, "Selects the buffer to work on")
}


while True :
	comm = raw_input("Editor (Buffer: %s @ %s)> " % (cur_buffer, Buffers[cur_buffer][1]))
	if not comm :
		continue

	tokens = comm.split()
	comm = tokens[0]

	args = [ autoconvert(tok) for tok in tokens[1:] ]
	if comm.lower() in commands.keys() :
		try :
			commands[comm][0](*args)
		except Exception as e:
			# print e
			print "Command '%s' needs more parameters. Check 'help'." % comm

	else :
		print "Command '%s' not found." % comm
		print "Type 'help' for a list of commands"


#	if comm == 'help' :
#		showHelp()
