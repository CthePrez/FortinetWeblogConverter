# LogParse recieves a typical Fortinet web filter report and converts it to CSV
# Charles Prezalor 4/27/2016

import argparse
import re
import sys

incoming_log_name = "log.log"
output_log_name = "log.csv"
linecount = 0

#Open the files for access
try:
	input_log = open(incoming_log_name, 'r')
	output_log = open(output_log_name, 'w')
except Exception as e:
	print(str(e))


def extract_headers(log_string):
	#extracts headers and writes them in CSV output file
	headers = ""
	for header in re.finditer('\s?(\w+)=',log_string):
		headers += header.group(1) + ","
	return headers

def extract_data(log_string):
	#extracts actual data from log strings
	log_data = ""
	for items in re.finditer('=(".*?"|.+?)\s',log_string):
		log_data += items.group(1) + ","
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
		headers = trim_string(extract_headers(entry))
		output_log.write(headers + "\n")
	log_entry = trim_string(extract_data(entry))
	output_log.write(log_entry + "\n")

print("Conversion completed!")
print(linecount, "lines processed")
