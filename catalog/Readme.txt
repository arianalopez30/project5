Readme.txt

Summary: This project uses flask and sqlalchemy to run a web application.

What is needed to run this app:
- download sqlalchemy and install it on the system that will run this application
- download the oauth files and install it on the system.

Run these commands in the cmd prompt to ensure your system is like mine
pip install werkzeug==0.8.3
pip install flask==0.9
pip install Flask-Login==0.1.3

-Before running the app the database will need to be created.
Open up the project folder from the command line. Follow these instructions:
1) Type python database.py (this will create the database and create a database.pyc file)
2) To populate the database run, python catalog_database_data.py
3) To run the app type