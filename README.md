# nimbus

## [Demo][demo]

## [Documentation][docs]

## Hardware Requirements

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

## Getting Started

### 1. [Install Docker Engine][docker-docs]

It works with Windows / macOS / [Linux (Ubuntu preferred). No need for any virtual machines. Docker handles all of our infrastructure/dependency needs.

### 2. [Install Docker-Compose][docker-compose-docs]

> Note: The previous step may have included the `docker-compose` binary depending on your operating system.

### 3. Clone this Repository

```
git clone https://github.com/mfekadu/nimbus
```

### 4. Run all the services

The following command will download/cache/install/build -- do everything to set up the infrastructure and run the program.

Run the following command in the root of the directory for this codebase:

```
docker-compose up
```

> Note: ElasticSearch needs a lot of memory. If it crashes, try increasing docker's memory allocation to >= 4GB.

> Note: Grab a coffee or some snacks. The various downloads will take some time, but docker will _*cache*_ each stage of the build, so things will be faster next time.

[demo]: #todo_insert_link
[docs]: #todo_insert_link
[docker-docs]: https://docs.docker.com/get-docker/
[docker-compose-docs]: https://docs.docker.com/compose/install/
[rasa-x-docs]: https://rasa.com/docs/rasa-x/installation-and-setup/docker-compose-script/
