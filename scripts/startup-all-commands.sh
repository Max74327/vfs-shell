# Startup script for stage 5 testing.
# Uses the paths that actually exist in data/vfs-nested.csv.

# --- ls / cd / who / head / tree (stage 4) ---
ls /
ls -l /home/user
ls -a /home/user
cd /
cd /home/user
cd projects
cd /
who
head /var/log/app.log
head -n 2 /var/log/app.log
head /home/user
head /no/such/file
tree -L 2 /home
tree -L 3 /home
tree -L 2 /no/such/path

# --- mv (stage 5) ---
mv /var/log/app.log /var/log/app.log.bak
ls /var/log
mv /var/log/app.log.bak /home/user
ls /home/user
ls /var/log
mv /no/such /var/log

# --- chmod (stage 5) ---
chmod 600 /var/log/app.log
ls -l /var/log
chmod u+x /var/log/app.log
ls -l /var/log
chmod go-w /var/log/app.log
chmod a=r /var/log/app.log
ls -l /var/log
chmod 1777 /var
ls -l /
chmod 9x9 /var/log/app.log
chmod 644 /no/such/file

# --- parsing and unknown commands ---
ls "unterminated
foo bar
cd a b

exit
