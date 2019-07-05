import pymysql
import hashlib
import re

conn = '101.132.226.19'
user = 'vehicleidentity'
pwd = '7rthFY8P3a5XWGT3'
db_name = 'vehicleidentity'
#charset = 'utf8'

'''
防止SQL注入攻击：使用参数带入方式，python会自动过滤args中的特殊字符，制止SQL注入的产生
'''
class DB(object):
    def __init__(self):
        self.db = pymysql.connect(conn, user, pwd, db_name)

    #查询一条数据
    def get_data_one(self,sql,args):
        cursor = self.db.cursor()
        try:
            cursor.execute(sql,args)
            result_one = cursor.fetchone()
        except Exception as ex:
            print(ex)
        return result_one

     #查询所有数据
    def get_data_all(self,sql,args):
        cursor = self.db.cursor()
        try:
            cursor.execute(sql,args)
            result_all = cursor.fetchall()
        except Exception as ex:
            print(ex)
        return result_all

    #增删改代码的封装
    def __edit(self, sql,args):
        cursor = self.db.cursor()
        count = 0
        try:
            count = cursor.execute(sql,args)
            self.db.commit()
        except Exception as ex:
            print(ex)
        return count

    #增
    def insert(self, sql, args):
        return self.__edit(sql, args)

    # 删
    def delete(self, sql, args):
        return self.__edit(sql, args)

    # 改
    def update(self, sql, args):
         return self.__edit(sql, args)

    #密码加密
    def my_md5(self, pwd):
        my_md5 = hashlib.md5()
        my_md5.update(pwd.encode('utf-8'))
        return my_md5.hexdigest()


    def close(self):
        self.db.close()