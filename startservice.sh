#!/bin/bash

export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:"/usr/lib/oracle/11.2/client64/lib"
export FORMS_HOME="${0%/*}"
ip='localhost'
port='8080'

test=$(curl --connect-timeout 25 --retry 3 --retry-delay 20 --write-out %{http_code} --silent --output /dev/null http://$ip:$port/)

if [[ "$test" -ne 200 ]]; then

  processes=$(ps aux | egrep "[p]ython.*run.py")
  if [[ -n "$processes" ]]; then

    for i in $processes
    do
      kill -9 $(echo $i | awk '{print $2}')
    done
  fi

  cd "$FORMS_HOME"
  ./run.py

fi
