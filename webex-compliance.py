# Copyright 2025 Clemens Geyer (clemens.geyer@gmail.com)
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import os, sys, csv, locale, re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

if (len(sys.argv) != 2):
	print("usage: [python3] {0} <report-id>-spaces.csv".format(sys.argv[0]))
	exit()

csvFileName = sys.argv[1]
spaceFolder = csvFileName[0:csvFileName.find("-spaces.csv")]

fileContent = {}
spaceNames = []

locale.setlocale(locale.LC_TIME,'en_US')

print("Trying to open CSV file '{0}'...".format(csvFileName))

# extract space names and types from CSV file
with open(csvFileName, 'r', newline='') as csvfile:
	fileContent = csv.DictReader(csvfile, fieldnames = ['spaceId','spaceName','classification','creationDate','activityCount','fileCount','whiteboardCount','totalFilesSizeInBytes','isOneOnOne','isPublic','ownedByExternalOrg','participantCount','participantDisplayNames 1-250','participantDisplayNames 251-500','participantDisplayNames 501-750','participantDisplayNames 751-1000','participantDisplayNames 1001-1250','participantDisplayNames 1251-1500','participantDisplayNames 1501-1750','participantDisplayNames 1751-2000','participantDisplayNames 2001-2250','participantDisplayNames 2251-2500','participantDisplayNames 2501-2750','participantDisplayNames 2751-3000','participantDisplayNames 3001-3250','participantDisplayNames 3251-3500','participantDisplayNames 3501-3750','participantDisplayNames 3751-4000','participantDisplayNames 4001-4250','participantDisplayNames 4251-4500','participantDisplayNames 4501-4750','participantDisplayNames 4751-5000','participantDisplayNames 5001-5250','participantDisplayNames 5251-5500','participantDisplayNames 5501-5750','participantDisplayNames 5751-6000'])
	for row in fileContent:
		if (row['isOneOnOne'] == 'false'):
			spaceNames.append([row['spaceId'],row['spaceName']])

		elif (row['isOneOnOne'] == 'true'):
			names = row['participantDisplayNames 1-250'].split(';')
			names[0] = names[0][0:names[0].find('<')]
			names[1] = names[1][0:names[1].find('<') - 1]
			
			spaceNames.append([row['spaceId'],'Direct Chat - ' + names[0] + '- ' + names[1]])

print('Extracted all necessary information, starting to rename files and folders...')

# switch to correct directory
os.chdir(spaceFolder)
os.chdir('spaces')

# go through every space / folder, read eml files and adjust time settings
for spaceId, spaceName in spaceNames:
	
	os.chdir(spaceId)
	
	# check every file in each folder
	for file in os.listdir():
		with open(file,'r') as f:
			content = f.read()
			# extract author of message (includes optional name part and mandatory email address)
			authorString = re.search(r'From: ([\w ]+)( <)?([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+.[a-zA-Z0-9-.]+>?)', content)
			# extract event date and time
			dateString = re.search(r'Date: (.* GMT)', content)

			# rename file so it contains author string
			newFileName = authorString.group(1) + ' - ' + file
			os.rename(file, newFileName)

			# create new date object and use it to update file time stamp according to event date and time
			newDate = datetime.strptime(dateString.group(1), '%a, %d %b %Y %H:%M:%S %Z')
			newDate = newDate.replace(tzinfo = ZoneInfo('GMT'))
			newDate = newDate.astimezone()
			os.utime(newFileName, times=(newDate.timestamp(), newDate.timestamp()))

	os.chdir('..')
	# rename directory to include space name or 1-to-1 conversation
	newDirName = spaceName + ' - ' + spaceId
	os.rename(spaceId, newDirName)
	print("Renamed folder to '{0}' and updated timestamp for all included files.".format(newDirName))

print('Done')
