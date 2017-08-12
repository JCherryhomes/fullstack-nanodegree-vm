'''
"Database code" for the DB Forum.
'''

import datetime
import psycopg2 as db


def create_connection():
    '''returns a tuple with connection and cursor'''
    connection = db.connect("dbname=forum")
    cursor = connection.cursor()
    return (connection, cursor)


def end_connection(connection):
    '''closes the cursor and connection'''
    connection.close()


def get_posts():
    """Return all posts from the 'database', most recent first."""
    (connection, cursor) = create_connection()
    cursor.execute("SELECT time, content FROM posts ORDER BY time DESC")
    posts = cursor.fetchall()
    end_connection(connection)
    return posts


def add_post(content):
    """Add a post to the 'database' with the current timestamp."""
    (connection, cursor) = create_connection()
    query = "INSERT INTO posts (content) values (%s)"
    data = (content, )
    cursor.execute(query, data)
    connection.commit()
    end_connection(connection)
