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
                message = f"User {username} Already exists"
            else:
                message = f"Failed to insert {username} with error {str(e.orig)}"
        return message
    def getUser(self, username):
        """
        Function to query an user from table users.
        input
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
        """
        q = self.db.execute(q, {"user":username})
        self.db.commit()
        return q,"Success"
