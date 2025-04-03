FROM postgres:14

COPY ./init-scripts/ /docker-entrypoint-initdb.d/

ENV POSTGRES_USER=rssuser
ENV POSTGRES_PASSWORD=rsspassword
ENV POSTGRES_DB=rssfeeds
