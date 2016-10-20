#!/usr/bin/env python

import sys
import os
import os.path
import re
import difflib
import copy
import argparse
import platform


#	pyminifier  --use-tabs --obfuscate-variables main.py > minified.py
#=====================================================================================================

def execTTY() :
	import pty
	# import tty
	# fileno = sys.stdin.fileno()
	# tty.setraw(fileno)
	# tty.setcbreak(fileno)
	pty.spawn( sys.argv )										# respawns the process in TTY
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

def isWindows() :
	return "windows" in platform.platform().lower()
#=====================================================================================================
if not sys.stdin.isatty() and not isWindows() : execTTY()	# checks if it executes in a TTY
print "[*] Got TTY: %s" % os.popen("tty").read().strip()

print 

Buffers = {}
#	changes, commands
UndoStacks = {}
CurrentBuffer = ''

parser = argparse.ArgumentParser("The (almost) non-interactive Editor (sudoedit compliant...)!")
parser.add_argument("file", nargs = '*', help = 'Files to be added in buffers.')
args = parser.parse_args()
# print args
if not args.file :
	file_lines = []
	buffername = "%s-(%s)" % ("Buffer", os.urandom(1).encode('hex') )
	Buffers[buffername] = (file_lines, None, None)
	UndoStacks[buffername] = ([], [], -1)
	CurrentBuffer = buffername
	# print ""

for file_ in args.file :
	# try :
	full_path = os.path.abspath(file_)
	if os.path.isfile(full_path) :
		file_handler = open(full_path, 'r')
		file_lines = file_handler.readlines()
		print "[+] File '%s' opened!" % file_
	else :
		print "[!] File: '%s' doesn't exist. Will be created when you save your buffer." % file_
		# file_handler = open(full_path, 'w')
		file_handler = None
		file_lines = []

	buffername = "%s-%s" % (full_path.split(os.path.sep)[-1], os.urandom(1).encode('hex') )
	Buffers[buffername] = (file_lines, full_path, file_handler)
	UndoStacks[buffername] = ([], [], -1)
	CurrentBuffer = buffername
		# sys.exit(-1)

	# except Exception as e:
	#	print e
	#	# print "Usage:"
	#	# print "	%s file_to_edit" % sys.argv[0]
	#	sys.exit(1)



def __askForConfirmation(message = "Are you sure?", yes = ['y', 'yes']) :
	option = raw_input("%s [y/N]" % message)
	return (option.lower() in yes)


#=====================================================================================================
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
	if stop > len(lines_) :
		stop = len(lines_)
	for number in range(start, stop) :
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
		print "[+] {0}\t- {1}".format(comm, commands[comm][1])
		try :
			 example = commands[comm][2]
			 print "ex. %s" % example 
		except :
			 pass
		print 
	print "=" * 20


def saveFileAs( given_filename = None ) :

	global Buffers
	if (given_filename == None) :
		filename = raw_input("Select filename/filepath to Save: ")
	else :
		filename = given_filename

	Buffers[ CurrentBuffer ] = ( Buffers[ CurrentBuffer ][0], filename, Buffers[ CurrentBuffer ][2] )
	saveFile()


def saveFile( ) :

	lines, filename, file = Buffers[ CurrentBuffer ]
	if filename == None :
		saveFileAs()
		return

	toSave = ''.join( lines )
	nlines = len( lines )
	try :
		file = open(filename, 'w')	# purge content
	except :
		print "Cannot write to '%s'. Didn't save." % filename
		return

	file.write(toSave)			 # write whole new content
	file.close()

	file = open(filename, 'r')	# reopen for reading ONLY
	Buffers[ CurrentBuffer ] = (lines, filename, file)
	print "Saved %d lines!" % nlines


def clearFile() :
	global lines
	lines = []
	print "The file is empty!"


def exitEditor() :
	global file
	for lines, filename, file in Buffers.values() :
		if file :
			 file.close()
	sys.exit(0)


def overwriteFile() :
	rand_str = os.urandom(8).encode('hex')
	print "You are about to overwrite the whole file."
	if not __askForConfirmation() :
		print "Aborted"
		return

	global lines
	lines = perLineWrite()
	print "Wrote %d lines! Changes HAVEN'T been saved" % (len(lines))


def writeFile( line = 0 ) :

	new_lines = perLineWrite()
	length = len(new_lines)
	print "You are about to replace:"
	print "="*20
	print displayFile( line, line+length )
	print "="*20
	print "With:"
	print displayFile( 0, length, lines_ = new_lines )
	
	if not __askForConfirmation() :
		print "Aborted"
		return
	global lines
	for index in range(line, line + length) :
		try :
			 lines [index] = new_lines[ index - line ]
		except :
			 lines.append ( new_lines[ index - line ] )


def perLineWrite() :
	rand_str = os.urandom(4).encode('hex')
	print "Type '%s' to return to Editor Prompt" % rand_str
	buffer = []
	i = 0
	line = ''
	while line.rstrip() != rand_str :
			 line = raw_input( "{:4}> ".format(i) )
			 buffer.append( line + os.linesep )
			 i += 1
	buffer = buffer[:-1]	 # remove the hash added at the end

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


def replaceKeyword(keyword, replacement = '', line = '*', instance = '*') :
	global lines

	if line == '*' :
		line_range =range( len(lines) )
	else :
		line_range = [line]

	for index in line_range :
		if instance != '*' :
			 splits = lines[index].split(keyword)
			 if len(splits) >= instance + 1 :
					before = keyword.join( splits[:instance] )
					after = keyword.join( splits[instance+1:] )
					ret = replacement.join( [before] + [after] )
			 else :
					ret = lines[index]
		else :
			 ret = lines[index].replace(keyword, replacement)
		lines[index] = ret


#=====================================================================================================

def bufferSelect ( buffer_ = None, sample = 3 ) :

	if buffer_ == None :
		print "Buffers:"

		for br in Buffers.keys() :
			 print "\t[-] {:<10} \t({:<4} lines) -\t@ file:{}".format \
					( br, len(Buffers[br][0]), Buffers[br][1]  )
			 displayFile( 0, sample, lines_ = Buffers[br][0] )
		return

	if buffer_ not in Buffers.keys() :
		Buffers[ buffer_ ] = ([], None, None)
		UndoStacks[buffer_] = ([], [], -1)
		print "Created new Buffer '%s'" % buffer_
	__changeToBuffer( buffer_ )
	print "Changed to buffer '%s'" % buffer_


def bufferCopy ( buffer_ ) :

	global Buffers
	if buffer_ in Buffers.keys() :
		if not __askForConfirmation() :
			 print "Aborted"
			 return
	Buffers[buffer_] = copy.deepcopy(Buffers[CurrentBuffer])
	UndoStacks[buffer_] = ([], [], -1)		# fresh new history
	print "Current buffer copied to '%s'" % buffer_


def __changeToBuffer( buffer_  ) :
	global lines
	global filename
	global file
	global CurrentBuffer
	lines, filename, file = Buffers[ buffer_ ] 
	global UndoIndex
	global UndoLast
	UndoStacks[CurrentBuffer] = (UndoStacks[CurrentBuffer][0], UndoStacks[CurrentBuffer][1], UndoIndex)
	UndoIndex = UndoStacks[buffer_][2]
	CurrentBuffer = buffer_
	UndoLast = ''


#=====================================================================================================
UndoLast = ''
UndoIndex = -1
ExcludeCommands = ['history', 'buffer', 'cpbuffer']
# ExcludeCommands = ['redo', 'undo', 'history']
def __findChanges() :
	if UndoLast == lines :
		return None
	try :
		diff = difflib.ndiff(UndoLast, lines)
		diff = list( diff )
	except :
		return None
	return diff

def __applyChanges( forward = False ) :

	global lines
	global UndoStacks
	global UndoIndex
	changes, stack, undoIndex = UndoStacks[CurrentBuffer]
	change = changes[UndoIndex]
	stack[UndoIndex]
	if forward :
		UndoIndex += 1
		lines = (''.join( difflib.restore(change, 2)) ).splitlines(1)
	else :
		UndoIndex -= 1
		lines = (''.join( difflib.restore(change, 1)) ).splitlines(1)
	print "Index: %d" % UndoIndex

def __undoReady() :
	global UndoLast
	# if not UndoLast :
	UndoLast = copy.deepcopy(lines)

def __undoRecord( comm, args ) :
	global UndoIndex
	if comm in ExcludeCommands :
		return
	args_ = ' '.join([str(arg) for arg in args])
	exec_line = "%s %s" % ( comm, args_ )
	changes, stack, undoIndex = UndoStacks[CurrentBuffer]
	change = __findChanges()
	if change == None :
		return
	if UndoIndex < len(stack) - 1 :
		stack[UndoIndex] = exec_line
		changes[UndoIndex] = change
	else :
		stack.append( exec_line )
		changes.append( change )
	UndoIndex += 1
	# UndoLast = ''	# to tell the Garbage Collection to delete the string copy
	# print diff


def undoChange() :
	if UndoIndex >= 0 :
		__applyChanges()
	else :
		print "No changes have been made!"

def redoChange() :
	if UndoIndex < len(UndoStacks[CurrentBuffer][0]) -1 :
		__applyChanges( forward = True )
	else :
		print "This is the last buffer version!"


def showHistory() :
	changes, stack, undoIndex = UndoStacks[CurrentBuffer]
	print
	if not changes :
		print "No history available!"
		return
	print "States : %d. Current State : %d" % (len(changes), UndoIndex+1)
	print "="*20
	undoIndex = 0
	hist_info = UndoStacks[CurrentBuffer][0:2]
	for change, command in zip( *hist_info ) :
		if undoIndex == UndoIndex :
			 arrow = '-->'
		else :
			 arrow = '  '

		print "%s Command: %s" % (arrow, command)
		for index, line in enumerate(change) :
			 if line.startswith('+') or line.startswith('-') :
					print "Line: %d> %s" %(index, line[:-1])
		undoIndex += 1
		print '-'*20
	print 

#=====================================================================================================


commands = {
"display" : (displayFile, "Displays the whole or a portion of the file.","display [starting_line] [ending_line]"), 
"edit" : (editLine, "Edit a specific line.","edit <line_to_edit>"),
"save" : (saveFile, "Save file changes."),
"saveas" : (saveFileAs, "Save buffer to new File.","saveas test.txt"),
"quit" : (exitEditor, "Exits the Editor"),
"help" : (showHelp, "Shows list of commands and examples"),
"less" : (lessFile, "A 'less' like way to view the file. Uses an optional 'step' argument", "less [number_of_lines]"),
"clear" : (clearFile, "Clears the whole file (doesn't automatically save)" ),
"overwrite" : (overwriteFile, "Lets you write the whole file from scratch using line-by-line editing"),
"swap" : (swapLines, "Swaps 2 lines by line number given as arguments", "swap <line> <line>"),
"search" : (searchLines, "Searches all lines for a keyword given as argument", "search <keyword>") ,
"regex" : (searchRegex, "Searces all lines for regex given as argument", "regex <python_regex>"),
"insert" : (insertLine, "Type the line to insert at the line number specified as argument (default appends the line to the file)", "insert [line_number]"),
"delete" : (deleteLine, "Deletes the line at the line number specified as argument", "delete <line_number>" ),
"replace" : (replaceKeyword, "Replaces a given keyword with a given replacement (defaults to ''). A specific line and instance of the keyword can be given as arguments.", "replace <keyword> <replacement> [line_number] [keyword_instance]" ),
"write" : (writeFile, "Starts a line editor and replaces the current buffer with the written content. The replacement starts from the line given as argument", "write [line_number]"),

"buffer" : (bufferSelect, "Selects the buffer to work on"),
"cpbuffer" : (bufferCopy, "Copies the Current Buffer to the specified on. Creates it if non-existent."),

"undo" : (undoChange, "Undoes the last change"),
"redo" : (redoChange, "Redoes the last change"),
"history" : (showHistory, "Displays history of the current buffer")
}


__changeToBuffer( Buffers.keys()[0] )

print

while True :
	try :
		comm = raw_input("Editor (Buffer: %s @ %s)> " % (CurrentBuffer, Buffers[CurrentBuffer][1]))
	except KeyboardInterrupt:
		print
		print "Pressed Ctrl+C. Type 'quit' to exit."
		comm = ''

	if not comm :
		continue

	tokens = comm.split()
	comm = tokens[0].lower()

	args = [ autoconvert(tok) for tok in tokens[1:] ]
	if comm in commands.keys() :
		try :
			 __undoReady()
			 commands[comm][0](*args)

		except Exception as e:
			 print sys.exc_info()
			 print "Command '%s' needs more parameters. Check 'help'." % comm
		__undoRecord(comm, args)

	else :
		print "Command '%s' not found." % comm
		print "Type 'help' for a list of commands or 'quit' to exit the Editor."
