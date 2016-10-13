import sys
import os

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
	file = open(filename, 'r+b')
except :
	print "Usage:"
	print "	%s file_to_edit" % sys.argv[0]
	sys.exit(1)


print "File to edit '%s'." % filename
lines = file.readlines()


def displayFile(start = 0, stop = None) :
	if stop == None :
		stop = len(lines)
	for number in range(start,stop+1) :
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
	print toSave
	file.write(toSave)
	file.flush()
	print "Saved!"


def exitEditor() :
	file.close()


commands = {
"display" : (displayFile, "Displays the whole or a portion of the file.\nExample: display [starting_line], [ending_line]"), 
"edit" : (editLine, "Edit a specific line.\nExample: edit <line_to_edit>"),
"save" : (saveFile, "Save file changes.\nExample: save"),
"exit" : (exitEditor, "Exits the Editor"),
"help" : (showHelp, "Shows list of commands and examples")
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


#	if comm == 'help' :
#		showHelp()
