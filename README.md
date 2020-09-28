# ChangeEngine

ChangeEngine is a tool for prioritizing your test runs based on saved test history.

Test history is stored in database using  [TestArchiver](https://github.com/salabs/TestArchiver).

And [Epimetheus](https://github.com/salabs/Epimetheus) is the tool for browsing the results you archived.

## Requirements

1) PostgreSQL database with archived result data.
2) `Python v3+`

## Database

Currently the only supported database engine is PostgreSQL. It can be local or cloud version.

Note that database should be different from what TestArchiver uses to store test result history. Both databases can be located on the same database server.

### Database schema

As the project is still in its alpha state, database must be created manually. You can use for example [pgAdmin](https://www.pgadmin.org/) to create a new database and then use [schema.sql](schema.sql) as schema template.

## Server component

Server component connects to database and waits for information about file changes.

First we have to configure the server with json config file. Template config file looks like this:

    {
        "db_name": "database_name",  # Use a different one from TestArchiver
        "db_host": "database_host_url",
        "db_user": "database_username",
        "db_password": "database_password",
        "port": server_listen_port
    }

Running server is done by passing the config file as an argument to `server.py`. Example run:

    python ./server.py config.json

Server should be running in port specified in configuration file.

## Feeding data to database


## Swagger docs

Swagger docs are readable from `http://localhost:port/doc/`. If you change APIs, please update swagger docs as well, thank you.

## Contribution

GitHub issues are welcome. We are interested in practical use cases.
