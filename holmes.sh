#!/bin/sh

echo "Holmes is running..."
while true
do
	echo "Press enter when next question is ready"
	read
	screencapture -R1314,140,345,340 question.png
	export GOOGLE_APPLICATION_CREDENTIALS=keys.json
	python script.py
done