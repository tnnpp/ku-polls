# Installation
### Clone or Download code from Github.
- You can clone the repository using this command
```
git clone https://github.com/tnnpp/ku-polls.git
```
- Or download the repository from my Github
### Create a virtual environment and install dependencies
1. Create virtual environment using this command.
```
virtualenv venv
```
if not install the virtualenv yet. Using this command 
```
pip install virtualenv
```
2. Activate the virtual environment
```
# On Linux or MacOS
source venv/bin/activate
# On MS Windows
venv\Scripts\activate
```
3. Installing Dependencies
```
pip install -r requirements.txt
```
### Set values for externalized variables
for convenient and security we are using python library python-decouple for externalized the variables

Create .env file in your project's root directory and put your data in this pattern. like in the sample.env file
```
SECRET_KEY = my-secret-key-value

# Set DEBUG to True for development, False for actual use
DEBUG = False

# ALLOWED_HOSTS is a comma-separated list of hosts that can access the app.
# You can use wildcard chars (*) and IP addresses. Use * for any host.
ALLOWED_HOSTS = *.ku.th, localhost, 127.0.0.1, ::1

# Your timezone
TIME_ZONE = Asia/Bangkok
```
### Run migrations
setting up the database by migration as the code fellows.
```
python manage.py makemigrations polls
python manage.py migrate polls
```
### Run Tests
to run the test for ensure the code are run correctly using this code.
```
python manage.py test polls
```
### Install data from the data fixtures
loading the data form user.json and polls.json into the application database using following code
```
python manage.py loaddata data/users.json data/polls.json
```
### How to running the appliction
Using following code
```
python manage.py runserver
```
More detailt of how to running the application is in [readme.md](https://github.com/tnnpp/ku-polls#readme)
