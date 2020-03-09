import os
import json
import sqlite3

# From: https://goo.gl/YzypOI
def singleton(cls):
    instances = {}

    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]

    return getinstance


class DatabaseDriver(object):
    """
    Database driver for the Task app.
    Handles with reading and writing data with the database.
    """

    def __init__(self):
        self.conn = sqlite3.connect("venmo.db", check_same_thread=False)
        self.create_task_table()

    def create_task_table(self):
        try:
            self.conn.execute("""
                CREATE TABLE users (
                    ID INTEGER PRIMARY KEY,
                    NAME TEXT NOT NULL,
                    USERNAME TEXT NOT NULL,
                    BALANCE DOUBLE(10,2) NOT NULL
                );
                """)
        except Exception as e:
            print(e)

    # Get all users
    def get_all_users(self):
        cursor = self.conn.execute("SELECT * FROM users;")
        users = []
        for row in cursor:
            users.append({'id':row[0],'name':row[1],'username':row[2]})
        return users

    # Add a user
    def insert_users_table(self, name, username, balance = 0):
        cursor = self.conn.cursor()
        cursor.execute('INSERT INTO users (name, username, balance) VALUES (?, ?, ?);',
        (name, username, balance))
        self.conn.commit()
        return cursor.lastrowid

    # Retrieve a user
    def get_user_by_id(self, id):
        cursor = self.conn.execute('SELECT * FROM users WHERE ID = ?', (id,))
        for row in cursor:
            return {'id':row[0],'name':row[1],'username':row[2],'balance':row[3]}

        return None

    # Delete a user
    def delete_user_by_id(self, id):
        self.conn.execute("""
            DELETE FROM users
            WHERE id = ?;
        """, (id,))
        self.conn.commit()

    # Update a user
    def update_user_by_id(self, id, balance):
        self.conn.execute("""
            UPDATE users
            SET balance = ? WHERE id = ?;
        """, (balance, id))
        self.conn.commit()
