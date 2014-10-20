#!/bin/bash
Stop(){
        PID=""
        for PID in `ps -eo pid,cmd |grep -E "nuri" |grep -v grep |sed 's/^ *//g'|cut -d " " -f 1`
        do
                kill -9 $PID
		echo "kill process $PID"
        done
}

Stop
