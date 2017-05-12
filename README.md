# UDPLogger

A service for logging messages to a SQL backend via UDP.

## Why UDPLogger?

UDPLogger was developed to allow you to decouple the saving of events and statistics to a secondary database from your main application.

UDP was chosen because it is lightweight and risk-free to emit and while it does not have the same reliability guarantees as TCP, it is more than adequate for non-critical event logging.

UDPLogger uses [SQLAlchemy](http://www.sqlalchemy.org/) to handle database connections and has been tested with MySQL, though other databases supported by SQLAlchemy should work as well. In the future, [Druid](http://druid.io/) will be supported as well.

An example use case would be to populate a database for analytics with [Caravel](http://airbnb.io/caravel/).

## Quick Start

### Server setup

### Defining tables

### Emitting data

## About

Developed and maintained by [Ivo Tzvetkov](https://github.com/ivotkv) at [ChallengeU](http://challengeu.com). Twitter: [@ivotkv](https://twitter.com/ivotkv). Gmail: ivotkv.

Copyright (c) 2016 Ivo Tzvetkov. Released under the terms of the [MIT License](https://opensource.org/licenses/MIT).
