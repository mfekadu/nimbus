# nimbus

## [Demo][demo]

## [Documentation][docs]

## Hardware Requirements

<details><summary>click to expand</summary>

The following requirements are [based on Rasa-X documentation][rasa-x-docs]

> vCPUs (virtual CPUs on Google Cloud Platform or equivalent number of cores)
>
> - Minimum: 2 vCPUs
> - Recommended: 2-6 vCPUs

> RAM
>
> - Minimum: 4 GB RAM
> - Recommended: 8 GB RAM

> Disk Space
>
> - Recommended: 100 GB disk space available

> Open These Ports (if running on Google Cloud Platform)
>
> - 22 (SSH)
> - 80 (HTTP)
> - 443 (HTTPS)

</details>

## Software Requirements

<details><summary>click to expand</summary>

> `Python 3.6.8` or newer

> `Docker 19.03.8` or newer

> `docker-compose 1.25.5` or newer

`$ python3 --version`

```
Python 3.6.8
```

`$ docker -v`

```
Docker version 19.03.8, build afacb8b
```

`$ docker-compose -v`

```
docker-compose version 1.25.5, build 8a1c60f6
```

</details>

## File Permissions

<details><summary>Ubuntu (GCP)</summary>

```
drwxrwxr-x 5 my_user_name my_user_name  4096 Jun 11 03:57 ./
drwxr-xr-x 5 my_user_name my_user_name  4096 Jun 11 03:57 ../
drwxrwxr-x 2 my_user_name my_user_name  4096 Jun 11 03:56 actions/
-rwxrwxr-x 1 my_user_name my_user_name    33 Jun 11 03:56 credentials.yml*
-rw-rw-r-- 1 my_user_name my_user_name    72 Jun 11 03:56 docker-compose.override.yml
-rwxrwxr-x 1 my_user_name my_user_name  4175 Jun 11 03:56 docker-compose.yml*
-rw-rw-r-- 1 my_user_name my_user_name   569 Jun 11 03:56 Dockerfile
-rwxrwxr-x 1 my_user_name my_user_name   652 Jun 11 03:56 endpoints.yml*
-rwxrwxr-x 1 my_user_name my_user_name   151 Jun 11 03:56 environments.yml*
drwxrwxr-x 8 my_user_name my_user_name  4096 Jun 11 03:56 .git/
-rw-rw-r-- 1 my_user_name my_user_name  1836 Jun 11 03:56 .gitignore
-rwxrwxr-x 1 my_user_name my_user_name  1782 Jun 11 03:56 install.sh*
-rwxrwxr-x 1 my_user_name my_user_name 35149 Jun 11 03:56 LICENSE*
-rwxrwxr-x 1 my_user_name my_user_name  3145 Jun 11 03:56 rasa_x_commands.py*
-rwxrwxr-x 1 my_user_name my_user_name  5796 Jun 11 03:56 README.md*
drwxrwxr-x 2 my_user_name my_user_name  4096 Jun 11 03:56 terms/
-rwxrwxr-x 1 my_user_name my_user_name   223 Jun 11 03:57 ubuntu_setup.sh*
```

</details>

<details><summary>macOS</summary>

> **NOTE:** the `1001` user is a PostgreSQL thing.

> **NOTE:** on Linux `wheel` == `root` ? ([Source][macos-wheel-group])

`$ ls -lah`

```
total 152
drwxr-xr-x  20 my_user_name  staff   640B Jun 10 19:21 ./
drwxr-xr-x  96 my_user_name  staff   3.0K Jun 10 16:39 ../
-rw-r--r--   1 my_user_name  staff   248B Jun 10 18:33 .env
drwxr-xr-x  15 my_user_name  staff   480B Jun 10 19:21 .git/
-rw-r--r--   1 my_user_name  staff   1.8K Jun 10 18:35 .gitignore
-rwxrwx---   1 my_user_name  wheel    34K Jun 10 16:39 LICENSE*
-rwxrwx---   1 my_user_name  wheel   3.2K Jun 10 18:42 README.md*
drwxr-xr-x   2 my_user_name  staff    64B Jun 10 19:45 actions/
drwxrwx---   2 my_user_name  wheel    64B Jun 10 19:21 auth/
drwxrwx---   2 my_user_name  wheel    64B Jun 10 18:57 certs/
drwxrwx---   2 my_user_name  wheel    64B Jun 10 18:57 credentials/
-rwxrwx---   1 my_user_name  wheel    33B Jun 10 18:54 credentials.yml*
drwxr-x---   2 1001          wheel    64B Jun 10 18:58 db/
-rwxrwx---   1 my_user_name  wheel   4.1K Jun 10 06:01 docker-compose.yml*
-rwxrwx---   1 my_user_name  wheel   652B Jun 10 18:54 endpoints.yml*
-rwxrwx---   1 my_user_name  wheel   151B Jun 10 18:54 environments.yml*
-rwxrwx---   1 my_user_name  wheel   1.7K Jun 10 17:23 install.sh*
drwxrwx---   2 my_user_name  wheel    64B Jun 10 18:58 logs/
drwxrwx---   2 my_user_name  wheel    64B Jun 10 18:57 models/
-rwxrwx---   1 my_user_name  wheel   3.1K Jun 10 06:01 rasa_x_commands.py*
drwxrwx---   3 my_user_name  wheel    96B Jun 10 18:58 terms/
```

</details>

## Getting Started

### **1. [Install Docker Engine][docker-docs]**

It works with [Windows][docker-desktop] / [macOS][docker-desktop] / [Linux (Ubuntu preferred).][docker-docs-ubuntu].

[Carl Boettiger][carl-b] suggests that Docker ["could
have promising implications for reproducible research in scientific communities"][docker-reproducibility] despite challenges like adoption by the scientific community. ([arxiv][docker-reproducibility-arxiv]).

### **2. [Install Docker-Compose][docker-compose-docs]**

> **NOTE:** The previous step may have included the `docker-compose` binary depending on your operating system.

### **3. Clone this Repository**

<details><summary>click to expand</summary>

```
git clone https://github.com/mfekadu/nimbus
```

</details>

### **4. Create the `.env` file with the following secrets**

<details><summary>click to expand</summary>

[The `.env` file is read by docker-compose][env-file-docs] (from _current working directory_) to string-replace the variables in the [`docker-compose.yml`][docker-compose-yml] file.

`$ cat .env`

```
# https://rasa.com/docs/rasa-x/installation-and-setup/docker-compose-manual/#environment-variables

# *****************************************************************************
# .............................................................................
# Global Environment Variables
# .............................................................................
# *****************************************************************************

# -----------------------------------------------------------------------------
# The version of Rasa X used by the Rasa X docker container.
# -----------------------------------------------------------------------------
RASA_X_VERSION=0.29.1

# -----------------------------------------------------------------------------
# The version of Rasa used by the Rasa docker containers.
# -----------------------------------------------------------------------------
RASA_VERSION=1.10.0

# -----------------------------------------------------------------------------
# Authentication token for the Rasa service. This is used by other services to communicate with Rasa.
# -----------------------------------------------------------------------------
RASA_TOKEN=random_string

# -----------------------------------------------------------------------------
# Authentication token for the Rasa X service. This is used by other services to communicate with Rasa X.
# -----------------------------------------------------------------------------
RASA_X_TOKEN=random_string

# -----------------------------------------------------------------------------
# Salt used to securely store the users passwords.
# -----------------------------------------------------------------------------
PASSWORD_SALT=random_string

# -----------------------------------------------------------------------------
# Symmetric JWT token for authentication protection of the Rasa API server.
# -----------------------------------------------------------------------------
JWT_SECRET=random_string

# -----------------------------------------------------------------------------
# Used by other services to access RabbitMQ.
# -----------------------------------------------------------------------------
RABBITMQ_PASSWORD=random_string

# -----------------------------------------------------------------------------
# Used by other services to access the PostgreSQL database.
# -----------------------------------------------------------------------------
DB_PASSWORD=random_string

# -----------------------------------------------------------------------------
# Used by other services to access Redis.
# -----------------------------------------------------------------------------
REDIS_PASSWORD=random_string

# -----------------------------------------------------------------------------
# If specified, this user with username RASA_X_USERNAME will be created immediately after Rasa X is started for the first time.
# Used to login to rasa-x dashboard
# -----------------------------------------------------------------------------
RASA_X_PASSWORD=random_string

# *****************************************************************************
# .............................................................................
# Rasa Variables
# .............................................................................
# *****************************************************************************

# -----------------------------------------------------------------------------
# How often to check for new models, in seconds
# -----------------------------------------------------------------------------
RASA_MODEL_PULL_INTERVAL=10

# -----------------------------------------------------------------------------
# Which Rabbit event queue to publish events to.
# -----------------------------------------------------------------------------
RABBITMQ_QUEUE=rasa_production_events
```

> **NOTE:** The `PASSWORD_SALT` is used to hash passwords. If you change this variable after setting it, you will have to create new logins for everyone. ([Source: Rasa Docs][rasa-x-docs])

</details>

### **4.5 Special Windows Step??**

<details><summary>TODO make sure this is true/needed</summary>

([Source][rasa-x-docs])

TODOs:

- [ ] make actions image a variable and put in `.env`
- [ ] can linux just use the `volumes:` too? if so, readme gets simplified.
- [ ] what about macOS?

`$ cat docker-compose.override.yml`

```
version: "3.4"

services:
  ...
  ...(other services)....
  ...
  app:
    image: mfekadu/rasa-actions:latest
  db:
    volumes:
      - db-volume:/bitnami/postgresql

volumes:
  db-volume:
    name: db-volume
```

</details>

### **4.96. Resources for Docker Desktop on (macOS / Windows)**

<details><summary>click to expand</summary>

![Docker Desktop Resources](/docs/assets/docker_desktop_resources.png)

</details>

### **5. Run all the services**

The following command will download/cache/install/build -- do everything to set up the infrastructure and run the program.

Run the following command in the root of the directory for this codebase:

```
docker-compose up -d
```

> **NOTE:** run with `sudo` if need be on Linux/macOS

> **NOTE:** Grab a coffee or some snacks. The various downloads will take some time, but docker will _*cache*_ each stage of the build, so things will be faster next time.

### **6. Set Username & Password**

```
python rasa_x_commands.py create --update admin me password
```

[demo]: #todo_insert_link
[docs]: #todo_insert_link
[docker-docs]: https://docs.docker.com/get-docker/
[docker-compose-docs]: https://docs.docker.com/compose/install/
[docker-desktop]: https://docs.docker.com/desktop/
[docker-docs-ubuntu]: https://docs.docker.com/engine/install/ubuntu/
[docker-reproducibility]: https://dl.acm.org/doi/10.1145/2723872.2723882
[docker-reproducibility-arxiv]: https://arxiv.org/abs/1410.0846v1
[carl-b]: https://scholar.google.com/citations?user=zj2rRtEAAAAJ
[rasa-x-docs]: https://rasa.com/docs/rasa-x/installation-and-setup/docker-compose-manual
[env-file-docs]: https://docs.docker.com/compose/env-file/
[docker-compose-yml]: /docker-compose.yml
[macos-wheel-group]: https://superuser.com/a/20430
