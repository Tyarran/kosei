rm -rvf $(find . -name "__pycache__" -type d)
rm -rvf .tox/
rm -rvf $(poetry show -v | grep Using | awk '{ print $3 }')
