from pydantic import BaseModel, EmailStr
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List
from datetime import date
from api.pgsql import Postgresql

class UserController():

    def register_user(self, body):
        pass

    def get_user_id(self, user_id):
        pass

    def write_oauth_user(self, user_id):
        pass