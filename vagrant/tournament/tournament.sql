-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP TABLE IF EXISTS MatchWinners;
DROP TABLE IF EXISTS Players;

CREATE DATABASE tournament;

CREATE TABLE Players (
    id serial PRIMARY KEY,
    name text
);

CREATE TABLE MatchWinners (
    id serial PRIMARY KEY,
    wins int,
    matches int,
    player_id int REFERENCES Players(id)
);
