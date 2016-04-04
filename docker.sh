#!/bin/bash
# Setup script for Cachet docker container
# From https://docs.cachethq.io/docs/get-started-with-docker
# with some changes to make it work...

export DB_USERNAME=cachet
export DB_PASSWORD=cachet
export DB_ROOT_PASSWORD=cachet
export DB_DATABASE=cachet
export APP_KEY=JHH7aXrVoVHuqUX62Pd0jLgx8rTMIUa2

docker run --name mysql -e MYSQL_USER=$DB_USERNAME -e MYSQL_PASSWORD=$DB_PASSWORD  -e MYSQL_ROOT_PASSWORD=$DB_ROOT_PASSWORD -e MYSQL_DATABASE=$DB_DATABASE -d mysql

docker run -d --name cachet --link mysql:mysql -p 80:8000 -e DB_HOST=mysql -e DB_DATABASE=$DB_DATABASE -e DB_USERNAME=$DB_USERNAME -e DB_PASSWORD=$DB_PASSWORD -e APP_KEY=$APP_KEY cachethq/docker:2.0.1

docker exec -it cachet php artisan app:install


