-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP TABLE IF EXISTS MatchWinners;
DROP TABLE IF EXISTS Tournaments;
DROP TABLE IF EXISTS Matches;
DROP TABLE IF EXISTS Players;
DROP DATABASE IF EXISTS tournament;

CREATE DATABASE tournament;

CREATE TABLE Players (
    id serial,
    name text
);

CREATE TABLE Matches (
    id serial,
    player_one_id int,
    player_two_id int
);

CREATE TABLE MatchWinners (
    id serial,
    wins int,
    matches int,
    player_id int
);

CREATE TABLE Tournaments (
    id serial
);
