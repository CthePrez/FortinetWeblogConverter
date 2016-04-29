# LogParse recieves a typical Fortinet web filter report and converts it to CSV
# Charles Prezalor 4/27/2016

import argparse
import re
import sys

#Configure Parser
parser = argparse.ArgumentParser(description='Converts Fortinet web logs into CSVs')
parser.add_argument("-i", metavar='filename', help="input log file name")
parser.add_argument("-o", metavar='filename', help="full output log in CSV format")
parser.add_argument("-w", metavar='filename', help="Minimal set of information for Web Logging")
args = parser.parse_args()

incoming_log_name = args.i
output_log_name = args.o
optimized_log = args.w
log_array = []
linecount = 0

#Open the files for access
if ((args.o and args.w) and (args.o == args.w)):
	print("Web and Output logs cannot be the same file.")
	sys.exit(1)

try:
	if args.i:
		input_log = open(incoming_log_name, 'r')
	if args.o:
		output_log = open(output_log_name, 'w')
	if args.w:
		web_log = open(optimized_log, 'w')
except Exception as e:
	print(str(e))
	sys.exit(1)



def extract_headers(log_string):
	#extracts headers and writes them in CSV output file
	headers = []
	for header in re.finditer('\s?(\w+)=',log_string):
		clean_header = ""
		for c in header.group(1):
			if c != '"':
				clean_header += c
		headers.append(clean_header)
	#Converts headers to string for return
	head_len = len(headers)
	x = 0
	headstring = ""
	for head_item in headers:
		headstring += head_item 
		if (x < head_len):
			headstring += ","
		x += 1
	return headstring

def extract_data(log_string):
	#extracts actual data from log strings
	log_data = []
	for items in re.finditer('=(".*?"|.+?)\s',log_string):
		clean_data = ""
		for c in items.group(1):
			if c != '"':
				clean_data += c
		log_data.append(clean_data)
	return log_data

def write_full_log():
	x=0
	tot_entries = len(log_array)		
	while x < tot_entries:
		#setting up variables to avoid trailing comma
		#z current number of elements processed in log array[x]
		z = 0
		tot_elements = len(log_array[x])
		for y in log_array[x]:
			z += 1
			#writing data to file
			try:
				output_log.write(str(y))
				if (z < tot_elements):
					output_log.write(",")
				else:
					output_log.write("\n")
			except Exception as e:
				print(str(e))
				print("Could not write to web log file " + args.o)
				sys.exit(2)
		x += 1


def write_web_log_headers():
	try:
		web_log.write("Date,Time,SourceIP,URL,Action,Category\n")
	except Exception as e:
		print(str(e))

def write_web_log(input_array):
	try:
		#Date
		web_log.write(input_array[0] + ",")
		#Time
		web_log.write(input_array[1] + ",")
		#Source IP
		web_log.write(input_array[10] + ",")
		#URL
		web_log.write(input_array[17] + "://" + input_array[18] + input_array[22] + ",")
		#Action
		web_log.write(input_array[20] + ",")
		#Category
		web_log.write(input_array[29] + "\n")
	except Exception as e:
		print(str(e))
		print("Could not write to web log file " + args.w)
		sys.exit(2)


#MAIN
#write web log headers
if args.w:
	 write_web_log_headers()

#Generate data array 
for entry in input_log:
	linecount += 1
	if linecount == 1:
		log_array.append([])
		log_array[0].append(extract_headers(entry))
	log_array.append([])
	log_array[linecount] = (extract_data(entry))
	#Fill Web Log with Data
	if args.w:
			write_web_log(log_array[linecount])

if args.o:
	write_full_log()


print("Conversion completed!")
print(linecount, "lines processed")

try:
	if args.i:
		input_log.close()
	if args.o:
		output_log.close()
	if args.w:
		web_log.close()
except Exception as e:
	print(str(e))
	sys.exit(1)