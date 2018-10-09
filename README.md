# FishPass
FishPass - Web Frontend Interface for OptiPass

## Installation
### Development Environment Only:
1. Create a project Directory
1. Clone marineplanner-core into it
1. Load Fishpass into MP core:
   * `cd marineplanner-core/apps`
   * `git clone https://github.com/Ecotrust/FishPass.git`

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
1. Set your Local Settings
   * TODO: see fishpass/local_settings.py.template
1. Import your data
   * To load initial data:  `dj loaddata /usr/local/apps/marineplanner-core/apps/FishPass/fishpass/fixtures/initial_setup.json`
   * To load an updated PAD file:
      * log in as an admin
      * Use this form: [http://localhost:8000/adminfishpass/import_PAD/](http://localhost:8000/adminfishpass/import_PAD/)
    * To load new FocusAreas:
       * run `dj import_focus_areas ZIPFILE TYPE` where:
          * `ZIPFILE` is a zipped shapefile in 3857
          * `TYPE` is on of the approved Focus Area types (see fishpass/project_settings.py `FOCUS_AREA_TYPES`)
          * example: `dj import_focus_areas /usr/local/apps/marineplanner-core/apps/FishPass/layers/counties.zip County`
             * County data is currently already included in loading the initial_data.json fixture
1. Enable Anonymous User
   * TODO: decide if this is a valid use case, document if so.
1. See steps below for installing OptiPass
   
### Production Server Setup:
#### Bootstrap MarinePlanner
1. `sudo apt-get update`
1. `sudo apt-get upgrade`
1. `sudo apt-get install git`
1. `mkdir /usr/local/apps`
1. `sudo chgrp adm /usr/local/apps`
1. `cd /usr/local/apps`
1. `git clone https://github.com/Ecotrust/marineplanner-core.git`

#### Install PostgreSQL/PostGIS and a few Dependencies
1. `cd /usr/local/apps/marineplanner-core/scripts/`
1. `sudo chmod +x vagrant_provision0.sh`
1. `sudo vagrant_provision0.sh xenial 3.6.2 9.5` #Ubuntu xenial, GEOS 3.6.2, PostgreSQL 9.5

#### Installing FishPass
```
cd /usr/local/apps/marineplanner-core/apps
git clone https://github.com/Ecotrust/FishPass.git
cd FishPass/scripts
chmod +x configure_project.sh
cp configure_project.sh /usr/local/apps/marineplanner-core/scripts/configure_project.sh
cd /usr/local/apps/marineplanner-core/scripts/
./configure_project.sh fishpass
cd /usr/local/apps/marineplanner-core/apps/FishPass/
./vagrant_provision.sh marineplanner-core marineplanner marineplanner /usr/local/apps/marineplanner-core/apps/FishPass/fishpass
/usr/local/apps/marineplanner-core/apps/mp-accounts/scripts/vagrant_provision.sh marineplanner-core
/usr/local/apps/marineplanner-core/apps/mp-visualize/scripts/vagrant_provision.sh marineplanner-core
/usr/local/apps/marineplanner-core/apps/madrona-scenarios/scripts/vagrant_provision.sh marineplanner-core
```
Activate the virtualenvironment and install the dependencies:
   * Note that I had run the 'finish the process' script before this - I'm not sure if the virtualenv exists yet, but it needs to.
```
source /usr/local/apps/marineplanner-core/env/bin/activate
pip install -e /usr/local/apps/marineplanner-core/apps/madrona-manipulators/
pip install -e /usr/local/apps/marineplanner-core/apps/madrona-scenarios/
pip install -r /usr/local/apps/marineplanner-core/apps/madrona-scenarios/requirements.txt
pip install -e /usr/local/apps/marineplanner-core/apps/mp-accounts/
pip install -r /usr/local/apps/marineplanner-core/apps/mp-accounts/requirements.txt
pip install -e /usr/local/apps/marineplanner-core/apps/mp-data-manager/
pip install -e /usr/local/apps/marineplanner-core/apps/mp-drawing/
pip install -r /usr/local/apps/marineplanner-core/apps/mp-drawing/requirements.txt
pip install -e /usr/local/apps/marineplanner-core/apps/p97-nursery/
pip install -r /usr/local/apps/marineplanner-core/apps/p97-nursery/requirements.txt
pip install -e /usr/local/apps/marineplanner-core/apps/madrona-analysistools/
```
Finish the process
`/usr/local/apps/marineplanner-core/scripts/vagrant_finish_provision.sh marineplanner-core marineplanner`

Create Shortcut 'dj':
1. `sudo vim /etc/bash.bashrc`
1. Add the following to the bottom of the script:
   ```
   alias dj="/usr/local/apps/marineplanner-core/env/bin/python /usr/local/apps/marineplanner-core/marineplanner/manage.py"
   alias djrun="dj runserver 0:8000"
   ```
1. now 'dj' will run 'manage.py' from wherever you are, without needing to activate your virtualenv
1. now 'djrun' will spin up your django server on port 8000
   * DO NOT USE THIS AFTER EARLY TESTING
   * NEVER RUN THIS WITH SUDO OR AS ROOT
   * CLOSE PORT 8000 AFTER TESTING


Load Data:
1. `dj loaddata /usr/local/apps/marineplanner-core/apps/FishPass/fishpass/fixtures/initial_setup.json`

#### Install Optipass
1. Get a copy of the OptiPass command line executable (c) Jesse O'Hanley
1. Copy it to /usr/local/apps/marineplanner-core/apps/FishPass/OptiPass/
   * NOTE: This directory will be available when Ryan merges the OptiPass branch in
1. `sudo chmod +x /usr/local/apps/marineplanner-core/apps/FishPass/OptiPass/OptiPassMain.out`
1. `sudo chmod 777 /usr/local/apps/marineplanner-core/apps/FishPass/fishpass/media`
1. [Install and Configure Instructions](https://github.com/Ecotrust/FishPass/wiki/Installing-OptiPass-Executable)


#### Import FocusAreas
1. `dj import_focus_areas /usr/local/apps/marineplanner-core/apps/FishPass/layers/counties.zip County`
   * you will have to change the file and supplied Focus Area type for other layers
   * See project_settings.py's FOCUS_AREA_TYPES for the other options

#### Install and Configure NGINX and UWSGI
1. Copy configuration script:
   * `ln -s /usr/local/apps/marineplanner-core/apps/FishPass/scripts/configure_production.sh /usr/local/apps/marineplanner-core/scripts/`
   * `cd /usr/local/apps/marineplanner-core/scripts/`
   * `sudo chmod +x configure_production.sh`
   * `./configure_production.sh`

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


