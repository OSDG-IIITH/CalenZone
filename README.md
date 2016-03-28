# CalenZone
#### IIIT Hyderabad Event Portal

CalenZone is an event tracker and manager created using Web2Py and JavaScript.

## Installation

- Install python-ldap module if not already installed 
    - Ubuntu
    `sudo apt-get install libsasl2-dev python-dev libldap2-dev libssl-dev`
    `pip install python-ldap`
    
- Git clone the repository into the applications folder of Web2Py and start web2py.

- Server Deployment
    - Rocket
        - Run web2py with `python web2py.py`
    - Apache
        - First time apache deployment(Overrides your sites-enabled configuration):-
        `wget http://web2py.googlecode.com/hg/scripts/setup-web2py-ubuntu.sh;`
        `chmod +x setup-web2py-ubuntu.sh;`
        `sudo ./setup-web2py-ubuntu.sh;`
        - Add to current Apache Setup(Doesn't override your sites-enabled configuration):-
            - Dependencies:-
                - Packages
                
                    apt-get -y install ipython
                    apt-get -y install python-dev
                    apt-get -y install postgresql
                    apt-get -y install apache2
                    apt-get -y install libapache2-mod-wsgi
                    apt-get -y install python2.5-psycopg2
                    apt-get -y install postfix
                    apt-get -y install wget
                    apt-get -y install python-matplotlib
                    apt-get -y install python-reportlab
                    apt-get -y install mercurial
                    /etc/init.d/postgresql restart


                - Modules
                
                    a2enmod ssl
                    a2enmod proxy
                    a2enmod proxy_http
                    a2enmod headers
                    a2enmod expires
                    a2enmod wsgi
                    a2enmod rewrite  # for 14.04
                    mkdir /etc/apache2/ssl

            - Add to your sites-enabled conf:-
            
```
WSGIDaemonProcess web2py user=www-data group=www-data processes=1 threads=1

<VirtualHost *:80>

  WSGIProcessGroup web2py
  WSGIScriptAlias / /home/www-data/web2py/wsgihandler.py
  WSGIPassAuthorization On

  <Directory /home/www-data/web2py>
    AllowOverride None
    Require all denied
    <Files wsgihandler.py>
      Require all granted
    </Files>
  </Directory>

  AliasMatch ^/([^/]+)/static/(?:_[\d]+.[\d]+.[\d]+/)?(.*) \
        /home/www-data/web2py/applications/$1/static/$2

  <Directory /home/www-data/web2py/applications/*/static/>
    Options -Indexes
    ExpiresActive On
    ExpiresDefault "access plus 1 hour"
    Require all granted
  </Directory>

  CustomLog /var/log/apache2/ssl-access.log common
  ErrorLog /var/log/apache2/error.log
</VirtualHost>

```


