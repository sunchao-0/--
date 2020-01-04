from flask import Flask
import pymysql


db = pymysql.connect(host='118.126.116.24', port=3306, user='root', passwd='root', db='videorent', charset='utf8')  # 创建链接


def data_db():  # 去数据库取数据，假设数据库表只有4个字段
    sql = """
          select * from user;
          """
    cc = db.cursor()  # 其实就是用来获得python执行Mysql命令的方法,也就是我们所说的操作游标
    cc.execute(sql)  # 真正执行sql语句
    cn = cc.fetchall()  # 接收全部的返回结果行row

    return cn  # 返回

app = Flask(__name__)


@app.route('/index')  # 设置路由
def index_list():  # 执行视图函数

    print("hello--------index----1")
    ret = data_db()  # 获取数据
    print(ret)
    print("hello--------index----2")

    return "hello"  # 返回response，浏览器会出现如下效果，如果返回其他，比如None就会只下载不在浏览器提示。


if __name__ == '__main__':
    app.run()