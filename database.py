from datetime import datetime
import logging
import sqlite3

from aiogram.types import Message


def create_db():
    with sqlite3.connect('db.db') as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS users (
                                                user_id INTEGER PRIMARY KEY UNIQUE,
                                                username TEXT UNIQUE,
                                                first_name TEXT,
                                                last_name TEXT,
                                                is_premium BOOLEAN DEFAULT 0,
                                                started_bot_at TEXT
                                                )"""
                  )
        c.execute("""CREATE TABLE IF NOT EXISTS petitions (
                                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                                author_id INTEGER,
                                                petition_text TEXT,
                                                message_id INTEGER,
                                                created_at TEXT,
                                                FOREIGN KEY (author_id) REFERENCES users(user_id)
                                                );"""
                  )
        conn.commit()


def add_user(message: Message):
    create_db()
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    is_premium = bool(message.from_user.is_premium)
    with sqlite3.connect('db.db') as conn:
        c = conn.cursor()
        try:
            c.execute("""INSERT INTO users (
                                            user_id,
                                            username,
                                            first_name,
                                            last_name,
                                            is_premium,
                                            started_bot_at
                                        ) VALUES (?, ?, ?, ?, ?, ?)""",
                      (
                          user_id,
                          username,
                          first_name,
                          last_name,
                          is_premium,
                          datetime.now(),
                      )
                      )
        except sqlite3.IntegrityError:
            c.execute(
                f"""UPDATE users 
                    SET first_name = ?,
                    last_name = ?,
                    username = ?,
                    is_premium = ? WHERE user_id = ?""",
                (
                    first_name,
                    last_name,
                    username,
                    user_id,
                    is_premium
                )
            )
        else:
            logging.info(f"User {username} added to database successfully")
        conn.commit()



def add_petition(message: Message):
    create_db()
    user_id = message.from_user.id
    petition_text = message.text
    message_id = message.message_id
    with sqlite3.connect('db.db') as conn:
        c = conn.cursor()
        c.execute("""INSERT INTO petitions (
                                        author_id,
                                        petition_text,
                                        message_id,
                                        created_at
                                    ) VALUES (?, ?, ?, ?)""",
                  (
                      user_id,
                      petition_text,
                      message_id,
                      datetime.now(),
                  )
                  )
        conn.commit()


def get_data(user_id: int):
    create_db()
    with sqlite3.connect('db.db') as conn:
        c = conn.cursor()
        user_data = c.execute(f"""SELECT * FROM users WHERE user_id = {user_id}""").fetchall()[0]
        user_petitions = c.execute(f"""SELECT * FROM petitions WHERE author_id = {user_id}""").fetchall()
        conn.commit()
    logging.debug(user_data)
    logging.debug(user_petitions)
    return user_data, user_petitions
