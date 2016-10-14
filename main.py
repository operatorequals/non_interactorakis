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
		print "[+] {0}\t- {1}\n".format(comm, commands[comm][1])
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

	file.write(toSave)			# write whole new content
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


def writeFile( line = 0 ) :

	new_lines = perLineWrite()
	# new_lines = perLineWrite().split( os.linesep )
	length = len(new_lines)
	print "You are about to replace:"
	print "="*20
	print displayFile( line, line+length )
	print "="*20
	print "With:"
	print displayFile( 0, length, lines_ = new_lines )
	option = raw_input("Are you sure? [y/N]")
	if not (option.lower() == 'y' or option.lower() == 'yes') :
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




Buffers = {'MAIN' : (lines, filename, file)}
#	changes, commands
UndoStacks = {'MAIN' : ([], [])}
CurrentBuffer = 'MAIN'

def bufferSelect ( buffer_ = None ) :

	if buffer_ == None :
		print "Buffers:"

		for br in Buffers.keys() :
			print "\t[-] {:<10} \t({:<4} lines) -\t@ file:{}".format \
				( br, len(Buffers[br][0]), Buffers[br][1]  )
			displayFile( 0, 2, lines_ = Buffers[br][0] )
		return

	if buffer_ not in Buffers :
		Buffers[ buffer_ ] = ([], None, None)
		print "Created new Buffer '%s'" % buffer_
	global CurrentBuffer
	CurrentBuffer = buffer_
	global lines
	global filename
	global file
	lines, filename, file = Buffers[ buffer_ ] 
	print "Changed to buffer '%s'" % buffer_




import difflib
import copy
UndoLast = []
UndoIndex = -1
def __findChanges() :
	if UndoLast == lines :
		return None
	try :
		diff = difflib.ndiff(UndoLast, lines)
		diff = list( diff )
		# global UndoLast
	except :
		return None
	return diff

def __applyChanges( forward = False ) :

	global lines
	global UndoStacks
	global UndoIndex
	print "Index: %d" % UndoIndex

	changes, stack = UndoStacks[CurrentBuffer]
	change = changes[UndoIndex]
	stack[UndoIndex]
	if forward :
		UndoIndex += +1
		lines = (''.join( difflib.restore(change, 2)) ).splitlines(1)
	else :
		UndoIndex += -1
		lines = (''.join( difflib.restore(change, 1)) ).splitlines(1)
	# print lines

def __undoReady() :
	global UndoLast
	# if not UndoLast :
	UndoLast = copy.deepcopy(lines)

def __undoRecord( comm, args ) :
	if comm == 'undo' or comm == 'redo' :
		return
	exec_line = "%s %s" % ( comm, ' '.join(args) )
	changes, stack = UndoStacks[CurrentBuffer]
	change = __findChanges()
	if change == None :
		return
	if UndoIndex < len(stack) -1 :
		stack[UndoIndex] = exec_line
		changes[UndoIndex] = change
	else :
		stack.append( exec_line )
		changes.append( change )
		global UndoIndex
		UndoIndex += 1
	# UndoLast = ''	# to tell the Garbage Collection to delete the string copy
	# print diff


def undoChange() :
	if UndoIndex >= 0 :
		__applyChanges()
	else :
		print "No changes have been made!"

def redoChange() :
	if UndoIndex < len(UndoStacks[CurrentBuffer][0]) - 1:
	# if len(UndoStacks[CurrentBuffer][0]) > 0 :
		__applyChanges( forward = True )
	else :
		print "This is the last buffer version!"



commands = {
"display" : (displayFile, "Displays the whole or a portion of the file.\nExample: display [starting_line], [ending_line]"), 
"edit" : (editLine, "Edit a specific line.\nExample: edit <line_to_edit>"),
"save" : (saveFile, "Save file changes.\nExample: save"),
"saveas" : (saveFileAs, "Save buffer to new File.\nExample: saveas test.txt"),
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
"replace" : (replaceKeyword, "Replaces a given keyword with a given replacement (defaults to ''). A specific line and instance of the keyword can be given as arguments." ),
"write" : (writeFile, "Starts a line editor and replaces the current buffer with the written content. The replacement starts from the line given as argument"),

"buffer" : (bufferSelect, "Selects the buffer to work on"),

"undo" : (undoChange, "Undoes the last change"),
"redo" : (redoChange, "Redoes the last change")
}


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
			__undoRecord(comm, args)

		except Exception as e:
			print e, sys.exc_info()
			print "Command '%s' needs more parameters. Check 'help'." % comm

	else :
		print "Command '%s' not found." % comm
		print "Type 'help' for a list of commands or 'quit' to exit the Editor."
