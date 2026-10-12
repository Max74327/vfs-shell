# Startup script for stage 5 testing.

# ls / cd / who / head / tree (stage 4)
ls /
cd /
ls -l /home/user
who
head -n 2 /home/user/notes.txt
tree -L 2 /home

# mv: rename, move into a directory, error cases
mv /home/user/notes.txt /home/user/notes.bak
ls /home/user
mv /home/user/notes.bak /tmp
ls /tmp
mv /home/user /home/user/projects
cd a b
mv /no/such/file /tmp

# chmod: octal, symbolic, special bits, error cases
chmod 600 /home/user/readme.md
ls -l /home/user
chmod u+x /home/user/readme.md
ls -l /home/user
chmod go-w /home/user/readme.md
chmod 1777 /tmp
ls -l /
chmod 9x9 /home/user/readme.md
chmod 644 /no/such/file

# exit
exit
