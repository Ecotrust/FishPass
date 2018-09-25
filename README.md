# FishPass
FishPass - Web Frontend Interface for OptiPass

## Installation
1. Create a project Directory
1. Clone marineplanner-core into it
1. Load Fishpass into MP core:
   * `cd marineplanner-core/apps`
   * `git clone https://github.com/Ecotrust/FishPass.git`
### Development Environment Only:
1. Configure app
   * *LINUX*
      * Copy apps/FishPass/scripts/configure_project.sh to scripts/configure_project.sh
   * *MAC*
      * Copy apps/FishPass/scripts/configure_project_mac.sh to scripts/configure_project.sh
   * make scripts/configure_project.sh executable
   * run your new configure_project script (may need to open in vim and enter :set fileformat=unix)
   * check that symlink to vagrant_provision.sh is created in marineplanner-core/scripts, not in marineplanner-core's root dir.
   * `vagrant up`
   * wait 30 minutes (or more if you don't have the base box or have a slow connection)
   * watch for errors and handle any that pop up - run `vagrant provision` to restart the provisioning process without losing all progress
   * run `vagrant reload` after installation to restart the server so all updates are applied
1. log in to the server with `vagrant ssh`
   * cd /usr/local/apps/marineplanner-core/
   * source env/bin/activate
   * cd marineplanner
   * python manage.py enable_sharing --all
   * python manage.py runserver 0:8000
### Production Environment Only
1. Install libraries: TODO
1. Load Data: TODO

### All Environments
1. Set your Local Settings
   * TODO: see fishpass/local_settings.py.template
1. Import your data
   * TODO: see [UCSRB Notes](https://github.com/Ecotrust/ucsrb#load-your-data)
      * Where to put files
      * What to run to import them
      * In what order
1. Enable Anonymous User
   * TODO: decide if this is a valid use case, document if so.
   
### Production Server Setup:
#### Install and Configure NGINX and UWSGI

```
sudo apt-get install nginx uwsgi uwsgi-plugin-python3 -y
pip install uwsgi

sudo cp /usr/local/apps/marineplanner-core/deployment/marineplanner_nginx.conf /etc/nginx/sites-available/marineplanner
sudo rm /etc/nginx/sites-enabled/default
sudo ln -s /etc/nginx/sites-available/marineplanner /etc/nginx/sites-enabled/marineplanner
sudo cp /usr/local/apps/marineplanner-core/deployment/uwsgi_params /etc/nginx/

sudo cp /usr/local/apps/marineplanner-core/deployment/emperor.ini /etc/uwsgi/
sudo ln -s /usr/local/apps/marineplanner-core/deployment/uwsgi.service /etc/systemd/system/
sudo ln -s /usr/local/apps/marineplanner-core/deployment/marineplanner.ini /etc/uwsgi/apps-enabled/

sudo chmod +x /usr/local/apps/marineplanner-core/deployment/restart_nginx.sh

sudo service uwsgi start
sudo service uwsgi restart
sudo cp /usr/local/apps/marineplanner-core/deployment/rc.local /etc/rc.local
```

#### Install and Configure Email
`sudo apt-get install postfix `
configuration:  
     Internet Site 
System mail name : 
     enter the domain name you plan to use, i.e.: s2f.ucsrb.org 

Then set Django settings to look something like this:
```
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = False
DEFAULT_FROM_EMAIL = 'MarinePlanner<marineplanner@your.domain>'
```
Configure DNS for secure delivery (see internal documentation)

#### Configure ReCaptcha and Registration
**NOTE: This does not seem required for the signup popup, only if user finds /account/** 
* pip install django-recaptcha
* Install with [these directions]https://github.com/praekelt/django-recaptcha#installation
* Use the 'NOCAPTCHA' setting (True)

#### Install and Configure Munin
```
sudo apt-get install munin munin-node
sudo vim /etc/nginx/sites-enabled/marineplanner
```

Between the `error_log` line and the `location /static ` line add:
```
location /munin/static/ {
        alias /etc/munin/static/;
}

location /munin {
        alias /var/cache/munin/www;
}
```

Then restart NGINX

```
sudo service nginx restart
```

#### Automatic (Unattended) Security Updates
From the document [Using the "unattended-upgrades" package](https://help.ubuntu.com/community/AutomaticSecurityUpdates#Using_the_.22unattended-upgrades.22_package)

Install the unattended-upgrades package if it isn't already installed:
```
sudo apt-get install unattended-upgrades
```

To enable it, do:
```
sudo dpkg-reconfigure --priority=low unattended-upgrades
```
(it's an interactive dialog) which will create `/etc/apt/apt.conf.d/20auto-upgrades` with the following contents:
```
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
```
To have the server automatically reboot when necessary to install security upddates:
1. install the package `update-notifier-common`
```
sudo apt-get install update-notifier-common
```
1. edit the file `/etc/apt/apt.conf.d/50unattended-upgrades` near the bottom you will find the line
```
//Unattended-Upgrade::Automatic-Reboot "false";
```
uncomment it and set value to true:
```
Unattended-Upgrade::Automatic-Reboot "true";
```
To tell the server what time is most safe to reboot (when needed), uncomment the line
```
//Unattended-Upgrade::Automatic-Reboot-Time "02:00";
```
And set the time to your desired restart time.

Read the source document for more details.


