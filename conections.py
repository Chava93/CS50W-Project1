from werkzeug.security import generate_password_hash,check_password_hash

class Users:
    """
    Class to connect to users db
    """
    def __init__(self, db):
        """
        db: sqlalchemy.orm.scoping.scoped_session
        Conection to db
        """
        self.db = db
    def insert_user(self, username, useremail, userpwd):
        """
        This function insert a new user in the User table.
        Input
        ------
        username, useremail, userpwd: strings
            corresponding to the user info
        """
        pwd = generate_password_hash(userpwd)
        try:
            q = self.db.execute("INSERT INTO users (username, email, pwdHash) VALUES (:user, :email, :pwd)",
                                {"user":username, "email":useremail, "pwd":pwd})
            message = f"User {username} successfully created."
            self.db.commit()
        except Exception as e:
            if "duplicate" in str(e.orig):
                message = f"User {username} or email {useremail} Already exists"
            else:
                message = f"Failed to insert {username} with error {str(e.orig)}"
        return message
    def getUser(self, username):
        """
        Get user by user name OR user email.
        -----
        username: str
            user name
        returns
        -------
        if user is not found: None
        Else: tuple
            (username, useremail, pwdhash)
        """
        q = """
            SELECT *
            FROM users
            Where username = (:user)
                OR email = (:user)
            """
        values = self.db.execute(q, {"user":username})
        return values.first()
    def validateUser(self, username, pwd):
        """
        Validate if a user is in the table users.
        inputs
        -----
        username: str
        pwd: str
        returns
        -------
        tuple containing (user_information, message)
        where user_informatio = None if user is not
        in table or enter wrong password.
        else
        user_info: dict
            with keys ['user', 'email']
        """
        user_info = self.getUser(username)
        # Case user does not exists
        if not user_info:
            message = "Not such user"
            return None, message
        user,email, ha = user_info
        valid_pwd = check_password_hash(ha, pwd)
        # Case suer enters invalid pwd
        if not valid_pwd:
            message = "Incorrect Password"
            return None, message
        # Case user log in correctly
        info = {"user":user, "email":email}
        return info, "Success"
    def deleteUser(self, username):
        q = """
        DELETE FROM users
        WHERE username = (:user)
            OR email = (:user)
        """
        q = self.db.execute(q, {"user":username})
        self.db.commit()
        return q,"Success"

class Books:
    """
    Class to connect to books db
    """
    def __init__(self, db):
        """
        db: sqlalchemy.orm.scoping.scoped_session
        Conection to db
        """
        self.db = db
    def get_book(self, search_info):
        """
        Given a book isbn, name and/or author make
            a query to the table users.
        -----
        search_info: dict
            with keys ["isbn","title","author"] and at
            least one value != None
        returns: Tuple: (list_of_results, message)
            list_of_results: list or None
            message: str
        """
        # Check that at least one value is not null
        if not any(search_info.values()):
            message = "You have to enter al least one value."
            return None,message
        # Filter keys with not None values
        info = [(k,v) for k,v in search_info.items() if v]
        # Create the query given the info
        patterns = list()
        for k,v in info:
            patterns.append(f"{k} SIMILAR TO '%{v}%'")
        patterns = " AND ".join(patterns)
        q = "SELECT * FROM books Where " + patterns
        ## Query Table books
        books = self.db.execute(q)
        books = books.fetchall()
        message = "" if books else "No book found. Please try again."
        return books, message
