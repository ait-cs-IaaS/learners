# Learners Environment ![workflow](https://github.com/ait-cs-IaaS/learners/actions/workflows/build.yaml/badge.svg)

Webinterface for accessing CR exercises.

## Build

```bash
python3 -m build
```

## Install

```bash
#pip
pip install https://github.com/ait-cs-IaaS/learners/releases/download/0.5.1/Learners-0.5.1.tar.gz

#docker
docker pull ghcr.io/ait-cs-iaas/learners
```

## Run

```bash
gunicorn --bind 127.0.0.1:5000 learners:app
# or
flask run
# or
docker-compose up -d
```

## Develop

```bash
pip install -e .
```


----------------
# Full deployment (including the exercise content)



## Install Dependencies
```bash
sudo apt install git docker-compose python3 hugo
```

## Create Folder structure
```bash
mkdir learners_env && cd learners_env
```

## CLone learners backend
```bash
git clone https://github.com/ait-cs-IaaS/learners.git
```

## Clone exercises-content
```bash
git clone https://<git-username>:<git-personal-access-token>@github.com/<exercises-repository> ./exercises-content && cd ./exercises-content
```

## build exercises content
```bash
./build.py -d ../learners/docker/learners/__webroot
```

## Copy the course Branding
```bash
cp course_branding/* ../learners/docker/learners/__templates/
```

## Change to directory
```bash
cd ../learners/docker/
```

## Copy the course Branding
Copy existing key and cert to docker/nginx/ssl/ or create new (if needed, adapt the `nginx.conf` file):
```bash
sudo openssl req -x509 -nodes -days 365 -newkey rsa:4096 -keyout nginx/ssl/itc.kr.key -out nginx/ssl/itc.kr.crt
```

## Build docker-compose
```bash
sudo docker-compose build
```

## Run docker-compose
```bash
sudo docker-compose up
```


----------------

# Final Folder structure


```bash
.
├── exercises-content
│   ├── archetypes
│   ├── build.py
│   ├── config                  # Hugo Environments
│   │   ├── base
│   │   ├── _default
│   │   ├── instructor
│   │   └── participant
│   ├── content                 # Hugo contents
│   │   ├── documentation
│   │   ├── exercises
│   │   └── presentations
│   ├── course_branding         # Learners styling
│   │   ├── login.html
│   │   ├── logo.html
│   .   └── theme_iaea.scss
│   .
│   .
│   └── themes
│       └── learners            # Theme (submodule)
│
└── learners
    ├── docker                  # Docker main
    │   ├── compose.yml         # Docker-Compose file
    │   ├── learners
    │   └── nginx
    ├── learners                # Source of backend
    │   ├── assets.py
    │   .
    │   .
    │   .
    │   └── templates
    ├── MANIFEST.in
    ├── pyproject.toml
    ├── README.md
    ├── setup.cfg
    └── setup.py
```
