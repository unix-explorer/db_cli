import mysql.connector
from getpass import getpass
import re

class DBHandler:
    def __init__(self):
        self.cnx = None
        self.cursor = None

    def connect(self, rootPasswd: str):
        """Establish connection to MySQL server"""
        try:
            self.cnx = mysql.connector.connect(
                host='localhost',
                user='root',
                password=rootPasswd,
                auth_plugin='mysql_native_password'  # Explicit auth plugin
            )
            self.cursor = self.cnx.cursor()
        except mysql.connector.Error as e:
            print(f"Connection error: {e}")
            raise

    def disconnect(self):
        """Properly close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.cnx:
            self.cnx.close()

    def validate_identifier(self, name: str) -> bool:
        """Validate database/user names to prevent SQL injection"""
        # Only allow alphanumeric and underscore, starting with letter
        pattern = r'^[a-zA-Z][a-zA-Z0-9_]*$'
        return bool(re.match(pattern, name))

    def create_new_user(self, newUserName: str, rootPasswd: str, password: str):
        """Create a new MySQL user with their own database"""
        # Validate inputs
        if not self.validate_identifier(newUserName):
            raise ValueError("Invalid username format. Use only letters, numbers, and underscores")
        
        if not password:
            raise ValueError("Password cannot be empty")
        
        try:
            self.connect(rootPasswd)
            
            # Create database with proper quoting
            query = f"CREATE DATABASE IF NOT EXISTS `{newUserName}`"
            self.cursor.execute(query)
            
            # Create user - MySQL automatically hashes the password
            query = "CREATE USER %s@'localhost' IDENTIFIED BY %s"
            self.cursor.execute(query, (newUserName, password))
            
            # Grant privileges
            query = f"GRANT ALL PRIVILEGES ON `{newUserName}`.* TO %s@'localhost'"
            self.cursor.execute(query, (newUserName,))
            
            # No need for FLUSH PRIVILEGES with CREATE USER/GRANT statements
            # FLUSH PRIVILEGES is only needed for direct grant table modifications
            
            self.cnx.commit()
            print(f"User '{newUserName}' created successfully")
            
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            if self.cnx:
                self.cnx.rollback()
            raise
        finally:
            self.disconnect()

    def delete_user(self, rootPasswd: str, userName: str):
        """Delete a MySQL user and optionally their database"""
        if not self.validate_identifier(userName):
            raise ValueError("Invalid username format")
        
        try:
            self.connect(rootPasswd)
            
            # Drop user
            query = "DROP USER IF EXISTS %s@'localhost'"
            self.cursor.execute(query, (userName,))
            
            # Optionally drop their database (uncomment if needed)
            # query = f"DROP DATABASE IF EXISTS `{userName}`"
            # self.cursor.execute(query)
            
            self.cnx.commit()
            print(f"User '{userName}' deleted successfully")
            
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            if self.cnx:
                self.cnx.rollback()
            raise
        finally:
            self.disconnect()

    def list_users(self, rootPasswd: str):
        """List all MySQL users"""
        try:
            self.connect(rootPasswd)
            query = "SELECT User, Host FROM mysql.user"
            self.cursor.execute(query)
            users = self.cursor.fetchall()
            return users
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            raise
        finally:
            self.disconnect()

    def change_password(self, rootPasswd: str, userName: str, newPassword: str):
        """Change password for a user"""
        if not self.validate_identifier(userName):
            raise ValueError("Invalid username format")
        
        try:
            self.connect(rootPasswd)
            query = "ALTER USER %s@'localhost' IDENTIFIED BY %s"
            self.cursor.execute(query, (userName, newPassword))
            self.cnx.commit()
            print(f"Password changed for user '{userName}'")
        except mysql.connector.Error as e:
            print(f"Database error: {e}")
            if self.cnx:
                self.cnx.rollback()
            raise
        finally:
            self.disconnect()