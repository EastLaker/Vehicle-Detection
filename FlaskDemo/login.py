# anther: 陈志鹏
import db_provider
import re
import getpass
# import captcha_generation

'''
用户名支持纯汉字和以字母开头的包含字母、数字、下划线的 1 —— 20 个字符
'''
# 汉字
RE_CHINESE = re.compile(r'^[\u4e00-\u9fa5]{1,20}$')
# 字母开头，包含字母，数字，下划线
RE_ALNUM = re.compile(r'^[a-zA-Z]\w{1,20}$')
'''
密码支持字母、数字、下划线的 6 —— 18 个字符
'''
# 字母，数字，下划线
RE_PASSWORD = re.compile(r'^\w{6,18}$')


class Sign(object):
    "用户注册和登录"
    def __init__(self):
        # 连接数据库
        db = db_provider.DB()
        # 使用预处理语句创建表
        sql = """CREATE TABLE IF NOT EXISTS user (
                                     name  CHAR(20) NOT NULL,
                                     pwd  CHAR(100) NOT NULL,
                                     PRIMARY KEY(name)) """
        db.db.cursor().execute(sql)

    # 注册
    def register(self, username, pwd, confirmpwd):
        # 连接数据库
        db = db_provider.DB()
        # 生成验证码图片
        # newcaptcha = captcha_generation.gen_captcha_text_and_image()

        if not RE_CHINESE.match(username) and not RE_ALNUM.match(username):
            return "输入的用户名（%s）不符合要求" % (username)
        sql = "SELECT COUNT(*) FROM user WHERE name = %s"
        ret = db.get_data_all(sql, username)
        if ret[0][0] > 0:
            return "用户名（%s）已经被占用,请更换用户名!" % (username)

        if not RE_PASSWORD.match(pwd):
            return "密码只能包含字母，数字，下划线，密码长度为6-18个字符"

        if pwd != confirmpwd:
            return "两次输入密码不相同"

        '''判断验证码是否正确
        for i in range(4):
            if captcha[i] != newcaptcha[i].upper() and captcha[i] != newcaptcha[i].lower():
                return "验证码错误"        
        '''

        # 执行注册功能
        args = (username, db.my_md5(pwd))
        sql = "INSERT INTO user(name,pwd) VALUES(%s,%s)"
        ret = db.insert(sql, args)
        if ret > 0:
            return '注册成功！'
        else:
            return '注册失败，请重新注册！'

    # 登录
    def login(self, username, pwd):
        # 生成验证码图片
        # newcaptcha = captcha_generation.gen_captcha_text_and_image()

        # 连接数据库
        db = db_provider.DB()

        '''
        for i in range(4):
            if captcha[i] != newcaptcha[i].upper() and captcha[i] != newcaptcha[i].lower():
                return "验证码错误"
        '''

        # 执行登录功能
        args = (username, db.my_md5(pwd))
        sql = "SELECT COUNT(*) FROM user WHERE name=%s and pwd=%s"
        ret = db.get_data_one(sql, args)
        if ret[0] > 0:
            return '登录成功！'
        else:
            return '登录失败，请重新登录！'










