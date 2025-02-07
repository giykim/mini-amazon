from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, address, balance):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.address = address
        self.balance = balance

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
            SELECT password, id, email, firstname, lastname, address, balance
            FROM Users
            WHERE email = :email
            """,
            email=email,
        )
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        # Check if user with specified email exists
        rows = app.db.execute("""
            SELECT email
            FROM Users
            WHERE email = :email
            """,
            email=email
        )
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname, address, seller):
        try:
            rows = app.db.execute("""
                INSERT INTO Users(email, password, firstname, lastname, address, balance)
                VALUES(:email, :password, :firstname, :lastname, :address, :balance)
                RETURNING id
                """,
                email=email,
                password=generate_password_hash(password),
                firstname=firstname,
                lastname=lastname,
                address=address,
                balance=0
            )

            id = rows[0][0]

            if seller:
                rows = app.db.execute("""
                    INSERT INTO Sellers(id)
                    VALUES(:id)
                    """,
                    id=id
                )

            return User.get(id)

        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))

            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
            SELECT id, email, firstname, lastname, address, balance
            FROM Users
            WHERE id = :id
            """,
            id=id
        )
        return User(*(rows[0])) if rows else None
    
    @staticmethod
    def update_info(id, password, firstname, lastname, email, address, balance):
        # check if email exists under different user
        email_unavailable = app.db.execute("""
            SELECT 1 
            FROM Users
            WHERE email = :email
                AND id <> :id
            """,
            id=id,
            email=email
        )
        # email already used, prevent email change
        if email_unavailable:
            return False

        # update user info based on user input
        rows = app.db.execute("""
            UPDATE Users 
            SET password = :password,
                firstname = :firstname,
                lastname = :lastname,
                email = :email,
                address = :address,
                balance = :balance
            WHERE id = :id
            """,
            id=id,
            password=password,
            firstname=firstname,
            lastname=lastname,
            email=email,
            address=address,
            balance=balance
        )

        return True

    @staticmethod
    def update_balance(id, balance):
        # set a user's balance
        rows = app.db.execute("""
            UPDATE Users 
            SET balance = :balance
            WHERE id = :id
            """,
            id=id,
            balance=balance
        )
