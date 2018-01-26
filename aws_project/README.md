# AWS Lightsail Information

### Public IP Address
```
18.218.232.136
```

### SSH Port
```
2200
```

#### HTTP Port
```
80
```

#### Web Application Link

[Web Application (http://18.218.232.136)](http://18.218.232.136)

#### Summary of Changes

- Added user grader
- Granted grader sudo privileges
- Made sure you could not remote in with passwords
- Removed ability to remote in as root
- Installed Apache2, pip, GIT and SQLite
- Configured web server
- Cloned catalog application
- Ran database_setup.py
- Created /var/www/html/myapp.wsgi to load catalog app
- Installed python libraries

#### Additional Notes
- I am running into an issue where I keep having to restart the apache2 service so if you go to the web site and it is not working then the service probably needs to be restarted
