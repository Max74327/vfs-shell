# Startup script for stage 4 testing.
# Covers all commands with valid and invalid inputs.

# ls: basic, flags, hidden, long, error
ls
ls /
ls -l /home/user
ls -a /home/user
ls -l -a /
ls /no/such/path
ls "unterminated

# cd: root, absolute, relative, error
cd /
cd /home/user
cd "projects"
cd /no/such/dir
cd a b

# who
who
who extra

# head
head /home/user/notes.txt
head -n 2 /home/user/notes.txt
head /home/user
head /no/such/file

# tree
tree /
tree -L 2 /home
tree /no/such/path

# exit
exit
