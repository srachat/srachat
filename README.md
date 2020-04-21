![Django CI](https://github.com/srachat/srachat/workflows/Django%20CI/badge.svg)

## How to install and run a backend manually

1) Clone the repo to some place at your local file storage
2) Navigate to the created project: `cd srachat`
3) Create `python virtual environment` by typing `python3 -m venv venv` (you can also try `python` or `py` instead of `python3`)
4) Activate the environment. Windows: `venv\Scripts\activate.bat`. Linux: `source venv/bin/activate`.
5) Install all needed requirements: `pip install -r requirements.txt`
6) Migrate the database: `py (python or python3) manage.py migrate`
7) Run server: `py (python or python3) manage.py runserver`

------------------------------------------------
Full instructions on `python venv` can be found here: https://docs.python.org/3/library/venv.html

## How to install and run a backend automatically by Docker

1) Install Docker Desktop on Windows from Docker Hub.
You can find it here: https://hub.docker.com/editions/community/docker-ce-desktop-windows/
2) Follow the instructions on the installation wizard to accept the license, authorize the installer, and proceed with 
the install. Some information you can find it here: https://docs.docker.com/docker-for-windows/install/
3) Test you installation - open a terminal window (CMD or PowerShell) and write: `docker --version` and  `docker run hello-world`.
More information: https://docs.docker.com/docker-for-windows/.
4) Clone the repo to some place at your local file storage
5) Navigate to the created project: `cd srachat`
6) If you startup Docker for our project for the first time, you have to startup it by `docker-compose up`. If any services
or the contents were added/changed you have to rebuild Docker by command `docker-compose build` and next startup it by `docker-compose up`.
7) Write to the browser's address bar localhost:8000/pidor/rooms/ and you can use it.