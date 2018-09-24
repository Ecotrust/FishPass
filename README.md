# FishPass
FishPass - Web Frontend Interface for OptiPass

## Installation
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
