# Проектная работа
__Тема__: Развертывание веб-приложения на базе  _Flask_ с использованием балансировки нагрузки средствами _Nginx_. Применение стека _Flask_ + _Nginx_ + _MySQL_.

## Структура проекта

<h5 align='center'>Стенд</h5>

![Scheme](img/Scheme.png)

Проект включает в себя следующую инфраструктуру серверов:

1. Балансировщики нагрузки (lb_01, lb_02)
    - Два сервера на базе **Nginx**, работающие в режиме балансировки нагрузки.   
    - Серверы делят между собой общий виртуальный IP-адрес, обеспечивая отказоустойчивость и высокую доступность (поддержка **Keepalived**).  

2. Серверы приложений (app_server_01, app_server_02)
    - Два сервера приложений, на которых развернуты **Docker-контейнеры** с приложением на базе **Flask**.    

3. Сервер базы данных (db_server_01)
    - Сервер базы данных на основе **MySQL**, обеспечивающий хранение и управление данными, используемыми приложением.  

Все серверы развернуты на виртуальных машинах, работающих под управлением **Ubuntu 24.04**.  

## Сервер баз данных
В качестве базы данных на сервере установлен MySQL.
После установки выполняем базовую настройку безопасности, устанавливая пароль root пользователю и уровень сложности:

```bash
proxima@db01:~$ mysql_secure_installation
```
Далее в настройках конфигурации MySQL изменить адрес подключения к базе данных. Это нужно для доступа нашего приложения с удаленной машины.

```bash
proxima@db01:~$ sudo cat /etc/mysql/mysql.conf.d/mysqld.cnf

[mysqld]
...
user            = mysql
port            = 3306

bind-address            = 0.0.0.0
mysqlx-bind-address     = 127.0.0.1

key_buffer_size         = 16M

myisam-recover-options  = BACKUP

log_error = /var/log/mysql/error.log

max_binlog_size   = 100M
...
```
Внести изменения:
```bash
sudo systemctl restart mysql
```

Создать базу данных и пользователя с доступом к ней:

```SQL
CREATE DATABASE database_name;
CREATE USER 'user_name'@'%' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON database_name.* TO 'user_name'@'%';
FLUSH PRIVILEGES;

```

## Сервер приложений

Для развертывания приложения на сервере должен быть установлен Docker и Docker Compose.

1. Склонировать репозиторий:
    ```bash
    git clone https://github.com/proxima-git/project_001.git
    ```
2. В корневой директории создать файл .env с переменными окружения для доступа к серверу БД:
    ```bash
    proxima@flaskapp1:~/project_001$ cat .env
    MYSQL_USER=user
    MYSQL_PASSWORD=password
    MYSQL_HOST=ip_adress
    MYSQL_PORT=3306
    MYSQL_DB=database_name
    ```
    где:
    + **user** - пользователь на сервере БД;
    + **password** - пароль для пользователя БД;
    + **ip_adress** - адрес хоста, где установлен MySQL;
    + **database_name** - название БД.

3. Собрать Docker образ, прописанный в Dockerfile:
    ```bash
    sudo docker compose build
    ```

4. Запустить контейнер:
    ```bash
    sudo docker compose up
    ```

Аналогично и для app_server_02.

## Балансировщик нагрузки

На сервере балансировки установлен nginx, который будет принимать http запросы, а также Keepalived для виртуального ip адреса.

1.  Конфигурационный файл nginx для приложения будет выглядеть следующим образом:

    ```bash
    proxima@web01:~$ sudo cat /etc/nginx/conf.d/project_001.conf

    upstream flask_backend {
        server ip_app_01:8080;
        server ip_app_02:8080;
    }


    server {
        listen 80;

        server_name ip_lb;

        location / {
                include uwsgi_params;
                uwsgi_pass flask_backend;
        }

    }

    ```
    где:
    + **ip_app_01/02** - ip адрес хоста, на котором развернуто приложение;
    + **ip_lb** - ip адрес балансировщика.

    В качестве алгоритма балансировки используется Round-robin для равномерного распределения запросов между серверами приложений.

    После внесения изменений:
    ```bash
    sudo nginx -t
    ```
    Если конфигурационный синтаксис в порядке:
    ```bash
    sudo systemctl restart nginx
    ```

2. Для доступа к балансировщику необходимо прописать правило в iptables:
    ```bash
    sudo iptables -A INPUT -p tcp --dport=80 -j ACCEPT
    sudo iptables -A INPUT -m state --state ESTABLISHED, RELATED -j ACCEPT
    ```
    Сохранить прописанные правила:
    ```bash
    sudo apt install iptables-persistent
    sudo netfilter-persistent save

    ```
    Аналогичная настройка nginx для lb_02

3. Конфигурационный файл для Keepalived:

    ```bash
    proxima@web01:$ sudo cat /etc/keepalived/keepalived.conf
    global_defs {
        enable_script_security
        }

    vrrp_script check_nginx {
        script "/usr/bin/systemctl is-active --quiet nginx"
        user keepalived_script
        interval 2
        weight 2
        }

    vrrp_instance vip_01 {
        state MASTER
        interface enp0s3
        virtual_router_id 51
        priority 101
        advert_int 1
        unicast_src_ip ip_web_01
        unicast_peer { ip_web_02 }

        authentication {
            auth_type PASS
            auth_pass somepass
            }

        virtual_ipaddress {
            ip-vrrp

            }

        track_script { check_nginx }

        }

    ```
    где:
    + **ip_web_01** - ip адрес lb_01;
    + **ip_web_02** - ip адрес lb_02;
    + **ip_vrrp** - виртуальный ip адрес.

    Создание пользователя keepalived_script для коректной работы скрипта проверки работоспособности nginx:
    ```bash
    sudo useradd -s /usr/sbin/nologin  keepalived_script
    ```
    Добавление записи протокола vrrp для правил iptables:
    ```bash
    sudo iptables -I INPUT -p vrrp -j ACCEPT
    netfilter-persistent save
    ```

    Аналогично и для lb_02, где параметр статуса виртуального ip меняется на **state BACKUP**, а также смена ip_web_01 на ip_web_02 и наоборот.
