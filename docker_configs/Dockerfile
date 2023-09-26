FROM ubuntu:20.04

RUN echo 'root:root' | chpasswd
RUN printf '#!/bin/sh\nexit 0' > /usr/sbin/policy-rc.d
RUN apt-get update && apt-get install -y systemd systemd-sysv dbus dbus-user-session
RUN printf "systemctl start systemd-logind" >> /etc/profile

RUN apt-get update && apt install tzdata
ENV TZ="Europe/Moscow"
RUN date

RUN apt-get update && apt-get install -y nano git curl mc gpg-agent net-tools

RUN curl -sL https://deb.nodesource.com/setup_18.x | bash && apt-get install nodejs

RUN curl -fsSL https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add - && echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-4.4.list

RUN apt update && apt install -y mongodb-org 

RUN printf " systemctl start mongod.service" >> /etc/profile

WORKDIR /home

COPY ./greet.sh ./home

EXPOSE 80/tcp 3000/tcp 3003/tcp 27017/tcp

ENTRYPOINT ["/sbin/init"]

