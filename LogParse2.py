# LogParse recieves a typical Fortinet web filter report and converts it to CSV
# Charles Prezalor 4/27/2016

import argparse
import re
import sys

incoming_log_name = "log.log"
output_log_name = "log2.csv"
optimized_log = "weblog2.csv"
log_array = []
linecount = 0

#Open the files for access
try:
	input_log = open(incoming_log_name, 'r')
	output_log = open(output_log_name, 'w')
	web_log = open(optimized_log, 'w')
except Exception as e:
	print(str(e))



def extract_headers(log_string):
	#extracts headers and writes them in CSV output file
	headers = []
	for header in re.finditer('\s?(\w+)=',log_string):
		clean_header = ""
		for c in header.group(1):
			if c != '"':
				clean_header += c
		headers.append(clean_header)
	return headers

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

def trim_string(input_string):
	#trims the trailing "," at the end of a string and removes double-quotes
	temp_string = ""
	if input_string[(len(input_string) - 1)] == "," :
		for c in range(0,(len(input_string) - 1)):
			if input_string[c] != "\"":
				temp_string += input_string[c]
		return temp_string
	else:
		return input_string


for entry in input_log:
	linecount += 1
	if linecount == 1:
		log_array.append([])
		log_array[0].append(extract_headers(entry))
	log_array.append([])
	log_array[linecount] = (extract_data(entry))
	#output_log.write(log_entry + "\n")

r=0
for l in log_array[1]:
	print(str(r) + ".", l)
	r += 1


print("Conversion completed!")
print(linecount, "lines processed")
