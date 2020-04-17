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
