# Battleship
This app is an implementation of a real-time battleship game written in Python (Django, Channels) and JavaScript (Vue).

# Demo
Because this app is hosted with a free heroku plan it gets unloaded from the server if it has not been used in last 30 minutes. This is why it takes some time to load when it is accessed for the first time in a while.

https://battleship-game-client.herokuapp.com/

# Requirements
- **Python 3.8** or higher
- **python3-dev** package
- **pipenv**
- **Docker** and **Redis**
- **Node.js v14** or higher and **npm**
- **PostgreSQL** configured as in settings.py DATABASES

# Quickstart
- Clone this repository.
- Backend:
    - Go to *server* folder.
    - Create a Python virtual environemnt and activate it with `pipenv shell`
    - Install dependencies with `pipenv install`
    - Apply migrations with `python manage.py migrate`
    - Start Redis server with `docker run -p 6379:6379 -d redis:5`
    - Run locally with `python manage.py runserver`
- Client:
    - Go to *client* folder.
    - Install node modules with `npm install`
    - Run locally with `npm start`
