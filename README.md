# py-teemoproject
Python wrapper to launch multiple [wkhtmltopdf](https://wkhtmltopdf.org/) binaries.
It uses [celery](http://www.celeryproject.org/) with [redis](https://redis.io) as broker.


## Build

To build a simple container.
```
docker build -t pyteemoproject .
```

A docker-compose.yml file is present for development purposes.
```
docker-compose up
```

## Configuration

The following environment variables are available:

|   Environment variable  |                                    default                                    |
|:-----------------------:|:-----------------------------------------------------------------------------:|
|       `RESULT_DIR`      |                                 `"/var/data"`                                 |
|     `REDIS_ADDRESS`     |                                 `"localhost"`                                 |
|       `REDIS_PORT`      |                                     `6379`                                    |
|    `WKHTMLTODPF_PATH`   |                         `"/usr/local/bin/wkhtmltopdf"`                        |
|    `WKHTMLTOPDF_ARGS`   | `"--quiet,--enable-external-links,--print-media-type,--javascript-delay,300"` |
| `WKHTMLTOPDF_FOOTERURL` |                                      `""`                                     |


## Development

```
docker-compose up
```

To add url to convert:
```
docker exec -it pyteemoproject_worker_1 python htmltopdf.py www.google.com
```
