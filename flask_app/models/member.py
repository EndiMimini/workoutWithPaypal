from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash
EMAIL_REGEX = re.compile(r'([A-Za-z0-9]+[.\-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Za-z]{2,})+')

PASWORD_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 


class Member:
    db_name = "workoutschema"
    def __init__(self, data):
        self.id = data['id']
        self.firstName = data['firstName']
        self.lastName = data['lastName']
        self.email = data['email']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']


    @classmethod
    def get_member_by_email(cls, data):
        query = 'SELECT * FROM members where email = %(email)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def approve(cls, data):
        query = 'UPDATE members set isVerified = 1 where id = %(id)s;'
        return connectToMySQL(cls.db_name).query_db(query, data)

    @classmethod
    def update_profile_pic(cls, data):
        query = "UPDATE members set profilePic = %(profilePic)s WHERE id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_member_by_id(cls, data):
        query = 'SELECT * FROM members where id = %(id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
        
    @classmethod
    def createPayment(cls,data):
        query = "INSERT INTO payments (ammount, status, member_id) VALUES (%(ammount)s, %(status)s, %(member_id)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def get_allUserPayments(cls, data):
        query = "SELECT * FROM payments where member_id = %(id)s;"
        results = connectToMySQL(cls.db_name).query_db(query, data)
        payments = []
        if results:
            for pay in results:
                payments.append(pay)
        return payments
        
    @classmethod
    def create(cls, data):
        query = "INSERT INTO members (firstName, lastName, email, password, verificationCode) VALUES (%(firstName)s, %(lastName)s, %(email)s, %(password)s, %(verificationCode)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM members where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)


    @staticmethod
    def validate_user(user):
        is_valid = True
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!", 'emailLoginMember')
            is_valid = False
        if len(user['password'])<1:
            flash("Password is required!", 'passwordLoginMember')
            is_valid = False
        return is_valid
    
    @staticmethod
    def validate_userRegister(user):
        is_valid = True
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!", 'emailRegister')
            is_valid = False
        if len(user['password'])<1:
            flash("Password is required!", 'passwordRegister')
            is_valid = False
        if len(user['firstName'])<1:
            flash("First name is required!", 'nameRegister')
            is_valid = False
        if len(user['lastName'])<1:
            flash("Last name is required!", 'lastNameRegister')
            is_valid = False
        return is_valid
    