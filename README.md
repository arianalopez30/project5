###1. Log into the virtual box in amazon
Arianas-MacBook-Pro:.ssh arianalopez$ ssh -i udacity_key.rsa root@52.34.162.177

###2. Create a new user named grader
```
sudo adduser grader
-password for grader is grader
-added sudoer access by going under /etc/sudoer.d and creating a file called grader.
In the grader file the following contents were placed and saved:
grader ALL=(ALL) NOPASSWD:ALL
```
Created public and private key pair for grader called project5.rsa
Passphrase is project5
```
Logged in as root, I switched to grader
root@ip-10-20-33-179:~# su grader
grader@ip-10-20-33-179:/root$ cd
grader@ip-10-20-33-179:~$ ls
grader@ip-10-20-33-179:~$ mkdir .ssh
grader@ip-10-20-33-179:~$ ls -la
total 24
drwxr-xr-x 3 grader grader 4096 Nov 22 18:03 .
drwxr-xr-x 3 root   root   4096 Nov 22 17:41 ..
-rw-r--r-- 1 grader grader  220 Nov 22 17:41 .bash_logout
-rw-r--r-- 1 grader grader 3637 Nov 22 17:41 .bashrc
-rw-r--r-- 1 grader grader  675 Nov 22 17:41 .profile
drwxrwxr-x 2 grader grader 4096 Nov 22 18:03 .ssh
grader@ip-10-20-33-179:~$ touch .ssh/authorized_keys
grader@ip-10-20-33-179:~$ cd .ssh
grader@ip-10-20-33-179:~/.ssh$ ls
authorized_keys
grader@ip-10-20-33-179:~/.ssh$ vi authorized_keys 
grader@ip-10-20-33-179:~/.ssh$ cd ..
grader@ip-10-20-33-179:~$ chmod 700 .ssh
grader@ip-10-20-33-179:~$ chmod 644 .ssh/authorized_keys 
grader@ip-10-20-33-179:~$ exit
```
Forcing Key Based Authentication
Was already set to no; no need to change anything

###3. Update all currently installed packages
sudo apt-get update
-Install package updates
root@ip-10-20-33-179:~# sudo apt-get upgrade

###4. Configure the local timezone to UTC
Machine is already set to UTC timezone
but to change this execute the following:
sudo dpkg-reconfigure tzdata, scroll to the bottom of the Continents list and select None of the Above; in the second list, select UTC
(http://askubuntu.com/questions/138423/how-do-i-change-my-timezone-to-utc-gmt)

###5.Change the SSH port from 22 to 2200
```
Changing ssh port
sudo ufw status
sudo ufw default deny incoming
sudo ufw default allow outcoming
sudo ufw allow ssh
sudo ufw allow www
sudo ufw allow ntp
```

modify /etc/ssh/sshd_config (http://ubuntuforums.org/showthread.php?t=1591681)
Change Port 22 to Port 2200 and save the file
Reload ssh service with sudo service ssh reload (https://help.ubuntu.com/community/SSH/OpenSSH/Configuring)
	(https://discussions.udacity.com/t/p5-how-i-got-through-it/15342)
	
###6. Configurethe UFW to only allow incoming connections for SSH, HTTP, and NTP
```
sudo ufw default deny incoming
sudo ufw default allow outcoming
sudo ufw allow ssh
sudo ufw allow www
sudo ufw allow ntp
sudo ufw allow 2200/tcp

sudo ufw enable
```

###7. Install apache2 to server a Python mod_wsgi application
Note: Originally I had an error when I tried to download apache2
root@ip-10-20-33-179:~# sudo apt-get install apache2
sudo: unable to resolve host ip-10-20-33-179
Reading package lists... Error!
E: Encountered a section with no Package: header
E: Problem with MergeList /var/lib/apt/lists/us-west-2.ec2.archive.ubuntu.com_ubuntu_dists_trusty-updates_main_i18n_Translation-en
E: The package lists or status file could not be parsed or opened.

Fixed it with this
```
cd /var/lib/apt
sudo mv lists lists.old
sudo mkdir -p lists/partial
sudo apt-get update
```

This will rebuild the cache.
http://ubuntuforums.org/showthread.php?t=1983220

Make a directory to store our project
cd /var/www
Jump to step 9 to install git
git clone https://github.com/arianalopez30/project5.git
cp -R project5/ catalog

Install Flask
sudo pip install Flask

Change the owner of the files for catalog
chown -R www-data:www-data catalog

Install mod_wsgi (https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps)
```
Configuring wsgi
create the wsgi file- catalog.wsgi
#!/usr/bin/python
import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/var/www/catalog/catalog')

from catalog import app as application
application.secret_key = 'Superman_is_awesome'
```
#############################
```
cd /etc/apache2/sites-available
vi catalog.conf
Added this to the file

<VirtualHost *>
	ServerName catalog.com
	WSGIDaemonProcess catalog user=grader threads=5
	WSGIScriptAlias / /var/www/catalog/catalog/catalog.wsgi
	<Directory /var/www/catalog>
		WSGIProcessGroup catalog
		WSGIApplicationGroup %{GLOBAL}
		Order deny,allow
		Allow from all
	</Directory>

</VirtualHost>
sudo a2ensite catalog.conf
sudo a2dissite 000-default

Restarted apache2
sudo service apache2 restart
```
Download sqlalchemy
```
pip install sqlalchemy (to test if my app works)
create new user:
sudo adduser catalog
password is linux
```
Alter the database.py
	python engine = create_engine('postgresql://catalog:Password@localhost/catalog')

Change the catalog.py too, like above.

###8. Install postgresSQL
```
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
```
By default no remote connections are allowed.
To ensure this I looked at view /etc/postgresql/9.3/main/pg_hba.conf 
```
su - postgres
CREATE USER catalog WITH PASSWORD 'linux';
ALTER ROLE catalog LOGIN; --To limit permissions
ALTER ROLE catalog CREATEDB;
```
Create the Database
CREATE DATABASE catalog WITH OWNER catalog;

Connect to the database
\c catalog

Added 2 categories
catalog=# INSERT INTO category (id, name) VALUES (1, 'Baseball');
catalog=# INSERT INTO category (id, name) VALUES (2, 'Soccer');

###9. Install git
https://www.digitalocean.com/community/tutorials/how-to-install-git-on-ubuntu-14-04
```
sudo apt-get install git
root@ip-10-20-33-179:~# git config --global user.name "Ariana Lopez"
root@ip-10-20-33-179:~# git config --global user.email "arianalopez30@hotmail.com"
root@ip-10-20-33-179:~# git config --list
```
To prevent the .git directory from being publicly accessible via a browser
go to the .htaccess file in the root of the web server and add
RedirectMatch 404 /\.git
http://stackoverflow.com/questions/6142437/make-git-directory-web-inaccessible

###10. My URL is http://ec2-52-34-162-177.us-west-2.compute.amazonaws.com


Getting OAuth to work
```
	Get my public ip address 52.34.162.177
	ec2-52-34-162-177.us-west-2.compute.amazonaws.com/
	Go to the Google Developers Console for project 3 (catalog)
	Click on Credentials and modify the Web Client 1
	Under Authorized JavaScript Origins add http://ec2-52-34-162-177.us-west-2.compute.amazonaws.com
	Under Authorized redirect URIs add http://ec2-52-34-162-177.us-west-2.compute.amazonaws.com/oauth2callback
	Save it
	Then download a new client_secrets.json and override the one on the Linux box
	I get an error from google 
	TypeError: <oauth2client.client.OAuth2Credentials object at 0x7f4995668d90> is not JSON serializable
	pip install werkzeug==0.8.3 pip install flask==0.9 pip install Flask-Login==0.1.3
	--Now I can sign in
```

Software I installed
```
 apt-get install finger
 sudo apt-get install apache2
 sudo apt-get install libapache2-mod-wsgi python-dev
 sudo apt-get install postgresql postgresql-contrib
 sudo apt-get build-dep python-psycopg2
 pip install psycopg2 
 pip install --upgrade google-api-python-client
``` 
 Fixed an error - was getting sudo: unable to resolve host ip-10-20-33-179 
 http://askubuntu.com/questions/59458/error-message-when-i-run-sudo-unable-to-resolve-host-none
 
 added my ipaddress to the /etc/hosts file for the 127.0.0.1 line
 
 
 
 Apache2 Notes
 By default, Ubuntu does not allow access through the web browser to any file apart of 
 those located in /var/www, public_html directories (when enabled) and /usr/share 
 (for web applications). If your site is using a web document root located elsewhere 
 (such as in /srv) you may need to whitelist your document root directory 
 in /etc/apache2/apache2.conf.
 
 The configuration system is fully documented in /usr/share/doc/apache2/README.Debian.gz.
