#!/bin/bash

usage()
{
cat << EOF
usage: $0 options

This script start a series of simulation of the ASR engine
varying the size of the data sended to the server (chunk) 

OPTIONS:
   -h      Show this message
   -w      Wav input
   -t 	   Timing input
   -s      Chunk start
   -e      Chunk end
   -i      Interval of chunk between 2 simulations
EOF
}


CHUNK_START=
CHUNK_END=
INTERVAL=
WAV=
TIMING=
while getopts “hs:e:i:w:t:” OPTION
do
     case $OPTION in
         h)
             usage
             exit 1
             ;;
         s)
             CHUNK_START=$OPTARG
             ;;

         e)
             CHUNK_END=$OPTARG
             ;;
         i)
             INTERVAL=$OPTARG
             ;;

         w)
             WAV=$OPTARG
             ;;

         t)
             TIMING=$OPTARG
             ;;
         ?)
             usage
             exit 
             ;;
     esac
done


if [[ -z $CHUNK_START || -z $CHUNK_END  || -z $INTERVAL || -z $WAV || -z $TIMING ]]
then
     usage
     exit 1
fi


if [ ! -f $WAV ]; 
then
    echo " Wav file not found!"
    exit 2
fi

if [ ! -f $TIMING ]; 
then
    echo " Timing file not found!"
    exit 2
fi



for (( i = $CHUNK_START; i <= $CHUNK_END; i+=$INTERVAL )); do
	./asr.py --subs yes --mode simulation --wav $WAV --timing $TIMING --chunk $i 
done
