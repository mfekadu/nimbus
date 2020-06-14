# nimbus

## [Demo][demo]

## [Documentation][docs]

## TL;DR;

### if ONLY CPU with Ubuntu 18.04 on Google Cloud Platform

> **NOTE:** 🙏 Please change the passwords in the `.env` file

```
git clone https://github.com/mfekadu/nimbus \
    && cd nimbus \
    && ./ubuntu_setup.sh \
    && cp .env_sample .env \
    && ./deploy.sh
```

### elif GPU with Ubuntu 18.04 on Google Cloud Platform

```
git clone https://github.com/mfekadu/nimbus \
    && cd nimbus \
    && ./gpu_setup.sh \
    && ./ubuntu_setup.sh \
    && cp .env_sample .env \
    && ./deploy.sh
```

### Else Keep Reading

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
> - 5002 (rasa-x)
> - 5065 (rasa-production)
> - 5075 (rasa-worker)
> - 5055 (app) (aka rasa-actions service)
> - 5432 (db) (postgres)
> - 5672 (rabbit)
> - 8000 (duckling)
> - 6379 (redis)
> - 9200 (elasticsearch-service)
> - 9300 (elasticsearch-service)
> - 9010 (nimbus-elastic-nlp-worker)

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

[The `.env` file is read by docker-compose][env-file-docs] (from _current working directory_) to string-replace the variables in the [`docker-compose.yml`][docker-compose-yml] file.

[**See the `.env_sample`**][env-sample]

TODOs:

- [ ] make actions image a variable and put in `.env_sample`

### **4.5. Resources for Docker Desktop on (macOS / Windows)**

<details><summary>click to expand</summary>

Sorry that this system is resource intensive. There may be room for optimization!

![Docker Desktop Resources](/docs/assets/docker_desktop_resources.png)

</details>

### **5. Run all the services**

The following command will download/cache/install/build -- do everything to set up the infrastructure and run the program.

Run the following command in the root of the directory for this codebase:

```
docker-compose up --detach
```

> **NOTE:** run with `sudo` if need be on Linux/macOS

> **NOTE:** Grab a coffee or some snacks. The various downloads will take some time, but docker will _*cache*_ each stage of the build, so things will be faster next time.

### **6. [Download the latest chatbot model][nimbus-models-folder]**

The latest model has the format `1-latest-YYYYMMDD-SSSSSS.tar.gz`

```
https://drive.google.com/drive/folders/1nUG5g63mPg3GN1CH1I6Z3uMUsMEQlOqS
```

### **7. Chat**

A custom chatbot UI can be found at

```
http://localhost
```

The chatbot admin page can be accessed after [logging in with `RASA_X_PASSWORD` found in `.env`][env-sample]:

```
http://localhost:5002
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
[env-sample]: /.env_sample
[nimbus-models-folder]: https://drive.google.com/drive/folders/1nUG5g63mPg3GN1CH1I6Z3uMUsMEQlOqS
