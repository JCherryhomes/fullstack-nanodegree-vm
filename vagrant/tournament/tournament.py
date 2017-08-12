#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2 as db


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection and cursor."""
    connection = db.connect("dbname=tournament")
    cursor = connection.cursor()
    return (cursor, connection)


def deleteMatches():
    """Remove all the match records from the database."""
    query = """
UPDATE MatchWinners
SET wins = 0, matches = 0; 
DELETE FROM Matches; 
DELETE FROM Tournaments;"""
    (cursor, connection) = connect()
    cursor.execute(query)
    connection.commit()
    connection.close()

def deletePlayers():
    """Remove all the player records from the database."""
    query = "DELETE FROM Players;"
    (cursor, connection) = connect()
    cursor.execute(query)
    connection.commit()
    connection.close()

def countPlayers():
    """Returns the number of players currently registered."""
    query = "SELECT COUNT(name) FROM Players"
    (cursor, connection) = connect()
    cursor.execute(query)
    count = cursor.fetchone()[0]
    if count is None:
        count = '0'
    connection.close()
    return long(count)

def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    query = '''
    INSERT INTO Players (name) VALUES (%(name)s); 
    INSERT INTO MatchWinners (player_id, wins, matches) 
    SELECT id, 0, 0 
    FROM Players 
    WHERE Players.id NOT IN (SELECT player_id FROM MatchWinners);'''
    (cursor, connection) = connect()
    cursor.execute(query, {'name':name,})
    connection.commit()
    connection.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    (cursor, connection) = connect()
    query = '''
    SELECT player_id, name, wins, matches 
    FROM MatchWinners 
    INNER JOIN Players
    ON Players.id = MatchWinners.player_id
    ORDER BY wins DESC;'''
    cursor.execute(query)
    results = cursor.fetchall()
    connection.close()
    return results

def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    (cursor, connection) = connect()
    query = """
UPDATE MatchWinners
SET wins = wins + 1,
    matches = matches + 1
WHERE player_id = %(winner)s;

UPDATE MatchWinners
SET matches = Matches + 1
WHERE player_ID = %(loser)s;
    """
    cursor.execute(query, {'winner': winner, 'loser': loser})
    connection.commit()
    connection.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    standings = playerStandings()
    results = []

    # Create two lists, one for the left side of the bracket and one for the right
    # Start at the first position of the current standings and grab every other entry
    first_group = standings[0::2]
    # Start at the second position of the standings and grab every other entry
    second_group = standings[1::2]

    # Zip the two groupings to create the pairings
    for left, right in zip(first_group, second_group):
        results.append((left[0], left[1], right[0], right[1]))

    return results
