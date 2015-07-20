#!/bin/bash
i=0
for file in $(ls tmp | grep .wav)
do
	filename="${file%.wav}.ref"
	sleep 1
	python ../kaldigstserver/client.py -r 4800 "tmp/$file" > $filename
done
