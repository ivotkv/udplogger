# UDPLogger

A service for logging messages to a SQL backend via UDP.

## Why UDPLogger?

UDPLogger was developed to allow you to decouple the saving of events and statistics to a secondary database from your main application.

UDP was chosen because it is lightweight and risk-free to emit and while it does not have the same reliability guarantees as TCP, it is more than adequate for non-critical event logging.

UDPLogger uses [SQLAlchemy](http://www.sqlalchemy.org/) to handle database connections and has been tested with PostgreSQL and MySQL, though other databases supported by SQLAlchemy should work as well.

## Quick Start

### Server setup

### Defining tables

### Emitting data

## About

Developed and maintained by [Ivo Tzvetkov](http://ivotkv.net) at [ChallengeU](http://challengeu.com).
