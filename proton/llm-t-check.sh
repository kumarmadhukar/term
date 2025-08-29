#!/bin/bash
# tool

#
# PROTON
# (C) 2022-2042, Kumar Madhukar
# Department of Computer Science and Engineering, Indian Institute of Technology Delhi
#


# A script wrapping around the term check python script to interface better with
# rest of proton

cd $TOOL_DIR

mkdir venv
cp -r venv-proton/* venv/
chmod -R 777 venv
mkdir tmp
chmod -R 777 tmp
mkdir logs
chmod -R 777 logs

LLM_GGUF=Llama-iproton.gguf # Where the model is stored
VENV_DIR=venv

# Delete symlinks if exist
#rm $VENV_DIR/bin/python*
#rm $VENV_DIR/lib64

# Get python bin
PY_BIN=$(which python3)
if [ -z "${PY_BIN}" ]
then
    echo "python3 not found"
    exit 22
fi

# Create symlinks
ln -s $PY_BIN $VENV_DIR/bin/python
ln -s $PY_BIN $VENV_DIR/bin/python3
ln -s $VENV_DIR/lib $VENV_DIR/lib64

# Update path of env so that it works on target
python3 virtualenv_tools.py --update-path auto $VENV_DIR

# Activate the venv
if [ ! -f $VENV_DIR/bin/activate ]
then
    echo "Activate script not found"
    exit 23
fi
source $VENV_DIR/bin/activate

# Call the code. TODO redirect output of this to /dev/null to quiet stuff
if ! command -v python >& /dev/null 
then
    echo "Python not found even after sourcing activate script"
    exit 24
fi 
python3 check_ter.py --in-file $BM_DIR/$1 --gguf $LLM_GGUF >& /dev/null

# Exit with code from last call
exit $?

