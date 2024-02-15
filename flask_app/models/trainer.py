from flask_app.config.mysqlconnection import connectToMySQL
import re
from flask import flash
EMAIL_REGEX = re.compile(r'([A-Za-z0-9]+[.\-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Za-z]{2,})+')

PASWORD_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 


class Trainer:
    db_name = "workoutschema"
    def __init__(self, data):
        self.id = data['id']
        self.firstName = data['firstName']
        self.lastName = data['lastName']
        self.email = data['email']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']


    @classmethod
    def get_all(cls):
        query = "SELECT * FROM trainers;"
        results = connectToMySQL(cls.db_name).query_db(query)
        trainers = []
        if results:
            for row in results:
                trainers.append(row)
        return trainers

    @classmethod
    def get_trainer_by_email(cls, data):
        query = 'SELECT * FROM trainers where email = %(email)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
    
    @classmethod
    def get_trainer_by_id(cls, data):
        query = 'SELECT * FROM trainers where id = %(id)s;'
        result = connectToMySQL(cls.db_name).query_db(query, data)
        if result:
            return result[0]
        return False
        
    
    @classmethod
    def create(cls, data):
        query = "INSERT INTO trainers (firstName, lastName, email, password, phone, speciality) VALUES (%(firstName)s, %(lastName)s, %(email)s, %(password)s, %(phone)s, %(speciality)s);"
        return connectToMySQL(cls.db_name).query_db(query, data)
    
    @classmethod
    def delete(cls, data):
        query = "DELETE FROM trainers where id = %(id)s;"
        return connectToMySQL(cls.db_name).query_db(query, data)


    @staticmethod
    def validate_user(user):
        is_valid = True
        if not EMAIL_REGEX.match(user['email']): 
            flash("Invalid email address!", 'emailLogin')
            is_valid = False
        if len(user['password'])<1:
            flash("Password is required!", 'passwordLogin')
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
        if len(user['speciality'])<1:
            flash("Speciality is required!", 'specialityRegister')
            is_valid = False
        if not user['phone']:
            flash("Last name is required!", 'phoneRegister')
            is_valid = False
        return is_valid
    