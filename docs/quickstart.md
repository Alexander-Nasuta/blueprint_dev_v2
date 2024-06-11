## Quickstart

### Pre-Requisites

- Python 3.9 or higher installed (in general it's recommended to use a environment manager like [conda](https://docs.anaconda.com/free/anaconda/install/windows/) or [venv](https://docs.python.org/3/library/venv.html))
- Docker installed (for example by installing [Docker Desktop](https://www.docker.com/products/docker-desktop/))
- A running Database (for example [MariaDB](https://mariadb.org/) or [MongoDB](https://www.mongodb.com/))

### Development Setup
The initial setup of the project is shown in the following video:

[![Project Setup](http://img.youtube.com/vi/WxKDhfsslRw/0.jpg)](http://www.youtube.com/watch?v=WxKDhfsslRw "Project Setup")

NOTE: to run database services you need to have a running database service (for example MariaDB or MongoDB) you need to provide some environment variables, that are used to connect to the database. 
NOTE: MongoDB needs to have a username and password set up, even if your MongoDB instance does not require authentication.

1. Clone this repository
2. If working with PyCharm you have to Mark the generated src directory as “Sources Root”.
3. Install the required dependencies with `pip install -r requirements.txt`
4. Run `mlflow server --host 127.0.0.1 --port 8080`
5. Run `fiot config` 
6. Run `fiot integration_test`
7. Start the individual services with by running the run.py files in the respective directories (for example `python src/database_mongo/run.py <<your enviorment vasriables>>`)
