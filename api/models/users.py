from pydantic import BaseModel, EmailStr
from traceback import format_exc
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.errors import UniqueViolation
from typing import List
from datetime import datetime, date, timezone
import bcrypt
from api.pgsql import Postgresql

class User(BaseModel):
    email: str = None
    pw: str = None
    first_name: str = None
    last_name: str = None
    phone: str = None
    gender: str = None
    dob: str = None
    zipcode: int = None
    user_id: int = None

    def hash_pw(self, password: str) -> str:
        salt = bcrypt.gensalt()
        # Hash the password with the salt
        hashed_password = bcrypt.hashpw(password.encode(), salt)
        return hashed_password

    def check_pw(self, stored_hash, pw_to_check):
        # Compare the stored hash with the hash of the entered password
        print(stored_hash)
        stored_hash = bytes(stored_hash)
        print(pw_to_check.encode())
        return bcrypt.checkpw(pw_to_check.encode(), stored_hash)
    def create_user(self, body):
        try:
            print('creating user')
            user_dob = body.dob.split('T')[0]
            user_pw = self.hash_pw(body.pw)
            print(user_pw)
            sql = f"""INSERT INTO healtheon.users
                                   (first_name, pw, last_name, gender, dob, phone, email, zipcode, active)
                                   values (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
            values = (body.first_name, user_pw,body.last_name, body.gender, user_dob, body.phone,
                        body.email, body.zipcode, 1)
            # print(sql)
            pg = Postgresql()
            conn = pg.connect()
            cur = conn.cursor()
            cur.execute(sql, values)
            conn.commit()
            conn.close()
            msg = {"message": "User created successfully", "code": 0}
            print(msg)
            return msg
        except UniqueViolation as uve:
            error_msg = format_exc()
            msg = {"message": "User not Created. Email already exists", "error": error_msg ,"code": 1}
            print(msg)
            return msg
        except Exception as e:
            error_msg = format_exc()
            msg = {"message": f"Failed to create user.", "error": error_msg,  "code": 1}
            print(msg)
            return msg

    def test_connection(self):
        pg = Postgresql()
        conn = pg.connect()
        print('connected')
        cur = conn.cursor()
        print('done')

    def get_user_id(self):
        pg = Postgresql()
        conn = pg.connect()
        cur = conn.cursor()
        sql = f"SELECT user_id FROM healtheon.users users WHERE email = '{self.email}'"
        cur.execute(sql)
        data = cur.fetchall()
        user_id = data[0][0]
        return {'user_id': user_id}

    def get_pw(self,):
        pg = Postgresql()
        conn = pg.connect()
        cur = conn.cursor()
        sql = f"SELECT pw, user_id FROM healtheon.users users WHERE email = %s"
        cur.execute(sql, (self.email,))
        data = cur.fetchall()
        print(data)
        return{'pw': data[0][0], 'user_id': data[0][1]}

    def authenticate_pw(self,):
        try:
            data = self.get_pw()
            pw = data['pw']
            user_id = data['user_id']
            authenticated = self.check_pw(pw, self.pw)
            if authenticated:
                return {'user_id': user_id, 'code': 0}
            else:
                return {'code': -1, "message": "Wrong password"}
        except IndexError:
            return {'code': -1, "message": "User does not exist. Please create an account."}
        except Exception as e:
            error_message = str(format_exc())
            msg = {'code': -1, "error": error_message, "message":"Something went wrong. Please try again later." }
            return msg

    def set_garmin_oauth_resource_owner(self, access_token):
        pass

    def store_auth_keys(self, user_id:int, resource_owner_key:str, resource_owner_secret:str):
        pg = Postgresql()
        conn = pg.connect()
        cur = conn.cursor()
        sql = f"""insert into healtheon.garmin_users (user_id, resource_owner_key, resource_owner_secret) 
                values (%s, %s, %s)"""
        cur.execute(sql, (user_id, resource_owner_key, resource_owner_secret,))
        conn.commit()
        msg = {'code': 0, 'message': 'Key stored successfully'}
        return msg

    def store_oauth_verifier(self, user_id:int, oauth_token:str, oauth_verifier:str):
        pg = Postgresql()
        conn = pg.connect()
        cur = conn.cursor()
        update_at = datetime.now(timezone.utc)
        sql = f"""update healtheon.garmin_users  
                set oauth_token = %s, 
                    oauth_verifier = %s,
                    updated_at = %s  
                where user_id = %s """
        cur.execute(sql, (oauth_token, oauth_verifier,update_at ,user_id,))
        conn.commit()
        msg = {'code': 0, 'message': 'Verifier stored successfully'}
        return msg

    def get_garmin_user_tokens(self):
        pg = Postgresql()
        conn = pg.connect()
        cur = conn.cursor()
        sql = f"""SELECT 
                    user_id, resource_owner_key, resource_owner_secret,
                    oauth_verifier, access_token, access_token_secret 
                    FROM healtheon.garmin_users WHERE user_id = %s"""
        cur.execute(sql, (self.user_id,))
        keys =['user_id', 'resource_owner_key', 'resource_owner_secret', 'oauth_verifier',
               'access_token', 'access_token_secret' ]
        values = cur.fetchall()[0]
        tokens = dict(zip(keys, values))
        return {'tokens': tokens, 'code': 0}

    def store_garmin_access_tokens(self, access_token, access_token_secret):
        pg = Postgresql()
        conn = pg.connect()
        cur = conn.cursor()
        update_at = datetime.now(timezone.utc)
        sql = f"""update healtheon.garmin_users  
                        set access_token = %s, 
                            access_token_secret = %s,
                            updated_at = %s  
                        where user_id = %s """
        cur.execute(sql, (access_token, access_token_secret, update_at, self.user_id,))
        conn.commit()
        msg = {'code': 0, 'message': 'Access Token stored successfully'}
        return msg

    def store_garmin_user_id(self, garmin_user_id):
        pg = Postgresql()
        conn = pg.connect()
        cur = conn.cursor()
        update_at = datetime.now(timezone.utc)
        sql = f"""update healtheon.garmin_users
                    set garmin_user_id = %s,
                        updated_at = %s
                    where user_id = %s """
        cur.execute(sql, ( garmin_user_id, update_at, self.user_id))
        conn.commit()
        msg = {'code': 0, 'message': 'Garmin User Stored Successfully'}
        return msg

if __name__ == '__main__':
    # user = User(email='jmac@test.com', first_name='test', last_name='test', phone='555555555', gender='Male',
    #              dob='01/01/2024', zipcode=32225, active=0)
    # user.create_user(user)
    # user.test_connection()
    user = User(email="jmccain@haylium.com", user_id=1)
    user.get_garmin_user_tokens()
