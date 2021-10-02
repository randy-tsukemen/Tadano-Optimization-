#!/bin/bash

SUBMIT=./submit

# make "submit" directory
if [ ! -e ${SUBMIT} ]; then
  echo "make ${SUBMIT}"
  mkdir ${SUBMIT}
  echo "make ${SUBMIT}/src"
  mkdir ${SUBMIT}/src
fi

# copy agent.py(and other files or directories) to "submit/src"
if [ ! -e ./agent.py ]; then
  echo "./agent.py does not exist. Try again."
  exit
else
  echo "copy ./agent.py to ${SUBMIT}/src"
  cp ./agent.py ${SUBMIT}/src
fi

# copy "model" to "submit"
if [ -e ./model ]; then
  echo "copy ./model to ${SUBMIT}"
  cp -r ./model ${SUBMIT}
else
  echo "make ${SUBMIT}/model"
  mkdir ${SUBMIT}/model
fi

# copy "requirements.txt" to "submit"
REQUIREMENTS=../requirements.txt
if [ -e ${REQUIREMENTS} ]; then
  echo "copy ${REQUIREMENTS} to ${SUBMIT}"
  cp ${REQUIREMENTS} ${SUBMIT}
fi

# compress "submit" in a zip file
echo "compress ${SUBMIT} in a zip file ${SUBMIT}.zip"
zip -r ${SUBMIT}.zip ${SUBMIT}
