# mensa
[![Push on Telegram](https://github.com/mattepica/mensa/actions/workflows/menu.yaml/badge.svg?branch=main)](https://github.com/mattepica/mensa/actions/workflows/menu.yaml)

## Setup
 ```bash
cp .env-simple .env
# Edit .env file
```

## Run once
 ```bash
docker run --env-file .env ghcr.io/mattepica/mensa:release
```
## Setup Crontab
 ```
30 07 * * 1-5 docker run --env-file .env ghcr.io/mattepica/mensa:release
```