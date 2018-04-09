#!/usr/bin/env bash

docker run --name mysql -e MYSQL_ROOT_PASSWORD=HON123well -d \
-p 3306:3306 \
-v /etc/mysql/conf.d:/etc/mysql/conf.d \
-v /var/lib/mysql:/var/lib/mysql
--restart always
mysql:5.7 \
--character-set-server=utf8 \
--collation-server=utf8_unicode_ci \
--max_allowed_packet=128M