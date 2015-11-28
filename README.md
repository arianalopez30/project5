# catalog
Project 3 for udacity nanodegree

Summary: This project uses flask and sqlalchemy to run a web application.

Files in the repo
-All of the files are in the catalog folder, except for the readme file.
-Within the catalog folder there are 2 folder, static (holds the style sheet for all web pages web app) and template folder (which contains the html templates used for the various html pages)
-The main file that holds all of the code and that will be used to run the application, is catalog.py (contains all of the methods)



What is needed to run this app:
- download sqlalchemy and install it on the system that will run this application
- download the oauth files and install it on the system.
Run these commands in the cmd prompt to ensure your system is like mine
	pip install werkzeug==0.8.3
	pip install flask==0.9
	pip install Flask-Login==0.1.3

-Before running the app the database will need to be created.
Open up the project folder from the command line. Follow these instructions:
1) Clone the repo, git clone https://github.com/arianalopez30/catalog.git
2) In the cmd prompt cd into the catalog directory where all the files are
1) Type python database.py (this will create the database and create a database.pyc file)
2) To populate the database run, python catalog_database_data.py
3) To run the app type: python catalog.py
4) Open Chrome and type localhost:8000/ (the app runs on port 8000)
5) Now you can peruse based on the links provided.
6) To see the json stuff type localhost:8000/catalog/json/
7) Congrats....I'm done!

=======
# project5
Linux Server Configuration - Udacity Project 5
