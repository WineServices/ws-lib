# Description
This library is used  fir shared c ode between different services

# Requirements:
Python version: 3.8



# Update Base dockerfile:

To update the base image:
- create locally the new image: `docker build -t wineservice/ws_lib -f DockerHubFile .`
- Open Docker Desktop and log in to Docker hub
- Go to images -> `wineservice/ws_lib`  -> Push to Hub


### Launch locally:

1- Create postgres database with docker: `docker-compose up -d`

2- Open `localhost:8000/docs` and you can try all routes.


# Developers section

- To install virtual environment: `export venv.sh`
- To launch unit tests: 

   1 - `source PYTHONPATH=<src-directory>`
   
   2- `pytest` 
