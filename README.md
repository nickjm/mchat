# ASAPP Backend Challenge

##### solution by Nick Matthews

## Description

Simple chat app built for ASAPP backend challenge. Supports account creation,
user login, sending messages, and fetching messages.

## Setup

1. Install Flask if needed with `pip install Flask`
2. Set you current flask app `export FLASK_APP=mychat.py`
3. Initialize the database `flask initdb`
4. Start the app with `flask run`
5. Finally, navigate to `localhost:5000` (or whatever flask is running at
  according to the feedback in your terminal)


Currently, only messages shown between the current user and the user "nick" show
up in the chat log, for simplicity. You'll need to create an account and
password first. In fact, the app is currently setup to require senders and
recipients to exist as users in order to send a message. Try following these
steps to get started:


1. Navigate to create account and create a user "nick"
3. Navigate back to create account (it redirects you) and create a user for
  yourself
4. Navigate to the login page and log yourself in
5. Send a message to "nick" via the home page
6. See that the messages appear in a below the new message area.

## Notes

Pagination is supported by the query convenience methods, but not surfaced on
the frontend. I also used a quick and dirty solution for the storing of
message type and metadata. I think if I were building something more permanent
I would have fields for height, width, duration and source; probably an ENUM
column for the type too, as I would be using a more capable database than
sqlite3

## Acknowledgments

Frontend code utilizes code and paradigms from
[Flaskr microblog][1]

[1]:	https://github.com/pallets/flask/tree/master/examples/flaskr
