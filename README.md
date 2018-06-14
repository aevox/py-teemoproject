# py-teemoproject
Python application that converts html pages to pdf and pushes them into an [owncloud](https://owncloud.org/) directory.
It is essentially a wrapper around [wkhtmltopdf](https://wkhtmltopdf.org/) and uses [celery](http://www.celeryproject.org/) with [redis](https://redis.io) as broker.


## Build

To build a simple container.
```
docker build -t py-teemoproject .
```

## Configuration

The following environment variables are available:

|   Environment variable  |                                    default                                  |
|:-----------------------:|:---------------------------------------------------------------------------:|
|     `REDIS_ADDRESS`     |                                 `localhost`                                 |
|       `REDIS_PORT`      |                                    `6379`                                   |
|        `REDIS_DB`       |                                     `0`                                     |
|    `WKHTMLTODPF_PATH`   |                         `/usr/local/bin/wkhtmltopdf`                        |
|    `WKHTMLTOPDF_ARGS`   | `--quiet --enable-external-links --print-media-type --javascript-delay 300` |
|      `OWNCLOUD_URL`     |                              `http://localhost`                             |
|     `OWNCLOUD_USER`     |                                   `admin`                                   |
|   `OWNCLOUD_PASSWORD`   |                                   `admin`                                   |
|    `OWNCLOUD_BASEDIR`   |                              `py-teemoproject`                              |


## Run

```
docker run --name py-teemoproject-app py-teemoproject
```

To add url to convert:
```
docker exec -it py-teemoproject-app python htmltopdf.py www.google.com remote/path/in/owncloud.pdf
```
If the path is not specified, the pdf will be written in `OWNCLOUD_BASEDIR`. The pdf name will be the md5sum of the url with the «.pdf» extension.

## Development

For development purposes a docker-compose.yml file is available.
It contains a Redis server and a Owncloud server.
```
docker-compose up
```
