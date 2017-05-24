# Fortigate Log Parser Version 3
# Charles Prezalor 5-17-2017
# Due to design flaws in the Fortigate Log Parser v2 that
# Made the application inflexible, I'm creating a version 3 that
# properly extracts the headers and holds them in a dictionary
# then saves the dictionary as a proper CSV

import argparse
import re
import sys
import time

#Configure Parser
parser = argparse.ArgumentParser(description='Converts Fortinet web logs into CSVs')
parser.add_argument("-i", metavar='filename', help="input log file name")
parser.add_argument("-o", metavar='filename', help="full output log in CSV format")
parser.add_argument("-w", metavar='filename', help="Minimal set of information for Web Logging")
args = parser.parse_args()

# FILE NAMES
str_RUNlogname = 'RunLog' + time.strftime("%Y%m%d%H%M%S") + '.txt'
str_FGlogname = args.i
str_CSVlogname = args.o
str_WEBlogname = args.w

# LISTS AND DICTIONARIES
list_FGlogfile = []
list_headers = []
dict_CSV_Table = {}
list_WEB_HEADERS = ['date','time','user','group','srcip','srcport','srcintf','dstip','dstport','dstintf','service','hostname','profile','action','reqtype','url','referralurl']


# Open the files for access
if ((args.o and args.w) and (args.o == args.w)):
	print("Web and Output logs cannot be the same file.")
	sys.exit(1)

# Initialize the log file
try:
	file_RUNlog = open(str_RUNlogname, 'w')
	file_RUNlog.write(time.strftime("%x %X ") + "Log Initialized" + '\n')
except Exception as e:
	# Print error and exit if otherwise failed
	print('Error Log could not be created!')
	print(str(e))
	sys.exit(1)

# Open files as listed in the args
try:
	if args.i:
		file_FGlog = open(str_FGlogname, 'r')
		file_RUNlog.write(time.strftime("%x %X ") + 'Opened FG log '+ str_FGlogname + '\n')
	if args.o:
		file_CSVlog = open(str_CSVlogname, 'w')
		file_RUNlog.write(time.strftime("%x %X ") + 'Initialized CSV log ' + str_CSVlogname + '\n')
	if args.w:
		file_WEBlog = open(str_WEBlogname, 'w')
		file_RUNlog.write(time.strftime("%x %X ") + 'Initialized WEB log ' + str_WEBlogname + '\n')
except Exception as e:
	file_RUNlog.write(time.strftime("%x %X ") + 'Error initializing logs' + '\n')
	file_RUNlog.write(time.strftime("%x %X ") + (str(e)) + '\n')
	print(str(e))
	sys.exit(1)

def Parse_FGlog_Line(str_FGlogline):
	# Accepts a string from the FG log and parses it into headers and content
	# returns a dictionary as header : data 

	dict_templine = {}
	
	# RegEx pattern: (\w+|\d+)=(".*?"|\S+)
	regex_FGsearch = re.compile(r'(\w+|\d+)=(".*?"|\S+)')

	list_re_FGlogline = regex_FGsearch.findall(str_FGlogline)

	for item in list_re_FGlogline:
		dict_templine[item[0]] = item[1].replace("\"","")
	
	return(dict_templine)


def Parse_FGlog_Headers():
	# collect all headers from the log entry list/dictionary
	# And compile them in a list

	# Itterate through each entry in the log table
	int_temp_linenum = -1
	for dict_entry in list_FGlogfile:
		int_temp_linenum += 1
		
		# and each item in each log entry
		int_temp_lineheader = -1
		for key in dict_entry:

			# Check and see if it's been added already.  If not, add it in the right place
			int_temp_lineheader += 1
			if str(key) in list_headers:
				# if it's in the header list, do nothing
				pass
			else:
				if int_temp_linenum == 0:
					# if it's in the first pass, just append it to the header list
					list_headers.append(str(key))
					file_RUNlog.write(time.strftime("%x %X ") + "P" + str(int_temp_linenum) + "H" + str(int_temp_lineheader) + " " + str(key) + " appended." + '\n')
				elif int_temp_linenum > 0:
					# if it's not the first pass, insert it in the right place
					list_headers.insert(int_temp_lineheader, str(key))
					file_RUNlog.write(time.strftime("%x %X ") + "P" + str(int_temp_linenum) + "H" + str(int_temp_lineheader) + " " + str(key) + " inserted." + '\n')
				else:
					# if neither condition is true, we have a problem.
					print("line index error " + str(int_temp_linenum))
					file_RUNlog.write(time.strftime("%x %X ") + "P" + str(int_temp_linenum) + "H" + str(int_temp_lineheader) + "Line error when parsing for headers." + '\n')
					sys.exit(0)

	file_RUNlog.write(time.strftime("%x %X ") + str(list_headers) + '\n')
	file_RUNlog.write(time.strftime("%x %X ") + "Headers list populated." + '\n')

def Build_CSV_Table():

	# Build the headers for the CSV Table
	for header in list_headers:
		dict_CSV_Table.update({header:[]})

	# for each log entry, for each header, pull the info from the log file
	# and populate it into the CSV table
	for entry in list_FGlogfile:
		for header in list_headers:
			try:

				if header in entry:
					# append the entry to the CSV table if it's in the entry
					dict_CSV_Table[header].append(entry[header])
				else:
					# Otherwise provide null since it's not part of the entry
					# But needs something in the CSV.
					dict_CSV_Table[header].append('')

			except IndexError as i:
				# This should only happen when trying to assign a value to the dict_CSV_Table
				# outside of the list's current range.  Should be using Append instead.  Fatal
				print("Index Error.")
				file_RUNlog.write(time.strftime("%x %X ") + str(i) + '\n')
				file_RUNlog.write(time.strftime("%x %X ") + "Attempted to modify value of non existing index in dict_CSV_Table." + '\n')
				sys.exit(1)
			except Exception as e:
				# General Error -- Fatal
				file_RUNlog.write(time.strftime("%x %X ") + str(e) + '\n')
				print(str(e))
				sys.exit(1)

	file_RUNlog.write(time.strftime("%x %X ") + "dict_CSV_Table populated. " + '\n')



def Write_CSV_File(int_TotEnt):
	# Uses the dict_CSV_Table to build a CSV file usable in excel or other
	# Spreadsheet programs.

	# Get number of headers
	int_totHead = len(list_headers)

	# Verify total number of entries
	if int_TotEnt == len(dict_CSV_Table[list_headers[0]]):
		# if the expected entries = the number of items in the table, good.
		pass
	else:
		# else, the issue is non-fatal, but should be corrected.  to avoid issues
		# changing the entry count to the actual length of entries.
		file_RUNlog.write(time.strftime("%x %X ") + "Expected length mismatch. Count:" + int_TotEnt + " List: " + len(dict_CSV_Table[list_headers[0]]) + '\n')
		int_TotEnt = len(dict_CSV_Table[list_headers[0]])

	# Write stats to the running log
	file_RUNlog.write(time.strftime("%x %X ") + "Creating CSV of " + str(int_totHead) + " colums and " + str(int_TotEnt) + " rows." + '\n')

	# Realized I needed to sanatize extra commas from URLs -- added .replace() to strings.

	# Write the headers to the CSV
	for header in list_headers:
		if header == list_headers[-1]:
			# if it's the last item write a newline instead of a comma
			file_CSVlog.write(str(header).replace(",", "") + '\n')
		else:
			file_CSVlog.write(str(header).replace(",", "") + ',')

	# Itterate through the entries in the table and write them, similar to above.
	for int_CSVLine in range(0,int_TotEnt):
		for header in list_headers:
			if header == list_headers[-1]:
				file_CSVlog.write(str(dict_CSV_Table[header][int_CSVLine]).replace(",", "%2C") + '\n')
			else:
				file_CSVlog.write(str(dict_CSV_Table[header][int_CSVLine]).replace(",", "%2C") + ',')


	file_RUNlog.write(time.strftime("%x %X ") + "Completed CSV File population." + '\n')


def Write_WEB_File(int_TotEnt):
	# Uses the dict_CSV_Table to build a WEB CSV file usable in excel or other
	# Spreadsheet programs.
	# special version that uses predefined headers from list_WEB_HEADERS

	# Get number of headers
	int_totHead = len(list_WEB_HEADERS)

	# Verify total number of entries
	if int_TotEnt == len(dict_CSV_Table[list_WEB_HEADERS[0]]):
		# if the expected entries = the number of items in the table, good.
		pass
	else:
		# else, the issue is non-fatal, but should be corrected.  to avoid issues
		# changing the entry count to the actual length of entries.
		file_RUNlog.write(time.strftime("%x %X ") + "Expected length mismatch. Count:" + int_TotEnt + " List: " + len(dict_CSV_Table[list_WEB_HEADERS[0]]) + '\n')
		int_TotEnt = len(dict_CSV_Table[list_WEB_HEADERS[0]])

	# Write stats to the running log
	file_RUNlog.write(time.strftime("%x %X ") + "Creating WEB CSV of " + str(int_totHead) + " colums and " + str(int_TotEnt) + " rows." + '\n')

	# Realized I needed to sanatize extra commas from URLs -- added .replace() to strings.

	# Write the headers to the WEB CSV
	for header in list_WEB_HEADERS:
		if header == list_WEB_HEADERS[-1]:
			# if it's the last item write a newline instead of a comma
			file_WEBlog.write(str(header).replace(",", "") + '\n')
		else:
			file_WEBlog.write(str(header).replace(",", "") + ',')

	# Itterate through the entries in the table and write them, similar to above.
	for int_CSVLine in range(0,int_TotEnt):
		for header in list_WEB_HEADERS:
			if header == list_WEB_HEADERS[-1]:
				file_WEBlog.write(str(dict_CSV_Table[header][int_CSVLine]).replace(",", "%2C") + '\n')
			else:
				file_WEBlog.write(str(dict_CSV_Table[header][int_CSVLine]).replace(",", "%2C") + ',')


	file_RUNlog.write(time.strftime("%x %X ") + "Completed WEB CSV File population." + '\n')








# MAIN PROGRAM

# initializes the line count for the number of lines in the file
int_TotalEntries = 0
for line in file_FGlog:
	int_TotalEntries += 1
	# send each line to Parse_FGlog_Line and append the returned dictionary to the log list
	list_FGlogfile.append(Parse_FGlog_Line(line))

# log the number of lines processed
file_RUNlog.write(time.strftime("%x %X ") + 'Processed ' + str(int_TotalEntries) + ' items from ' + str_FGlogname + ' \n')

# extract headers in order in a list
Parse_FGlog_Headers()

# Use header list to build CSV table
Build_CSV_Table()

# use CSV table to produce file output
if args.o:
	Write_CSV_File(int_TotalEntries)

# Use custom header list to produce web log
if args.w:
	Write_WEB_File(int_TotalEntries)

# Close files and Tidy up
try:
	if args.i:
		file_FGlog.close()
		file_RUNlog.write(time.strftime("%x %X ") + 'Closed FG log '+ str_FGlogname + '\n')
	if args.o:
		file_CSVlog.close()
		file_RUNlog.write(time.strftime("%x %X ") + 'Closed CSV log ' + str_CSVlogname + '\n')
	if args.w:
		file_WEBlog.close()
		file_RUNlog.write(time.strftime("%x %X ") + 'Closed WEB log ' + str_WEBlogname + '\n')
except Exception as e:
	file_RUNlog.write(time.strftime("%x %X ") + 'Error Closing logs' + '\n')
	file_RUNlog.write(time.strftime("%x %X ") + str(e) + '\n')
	print(str(e))
	sys.exit(1)

try:
	file_RUNlog.write(time.strftime("%x %X ") + 'END OF LOG.' + '\n')
	file_RUNlog.close()
except Exception as e:
	print(str(e))
	sys.exit(1)

sys.exit(0)