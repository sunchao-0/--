from flask_jsglue import JSGlue
import random
from uuid import uuid1
from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy

import pymysql
from flask_restful import reqparse, abort, Api, Resource

app = Flask(__name__)
api = Api(app)
# 数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@127.0.0.1:3306/book?charset=utf8mb4'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 前端请求后端
js_glue = JSGlue()
js_glue.init_app(app)  # 让js文件中可以使用url_for方法

# 获取请求（get post put）
parser = reqparse.RequestParser()

# 数据库模型类
class Customer(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=True)
    phoneNumber = db.Column(db.String(20), unique=True)
    deposit = db.Column(db.String(10))
    comment = db.Column(db.String(50))

    def __init__(self, customer_id=None, customer_name=None, customer_phone=None, customer_deposit="0", comment=""):
        self.id = customer_id
        self.name = customer_name
        self.phoneNumber = customer_phone
        self.deposit = customer_deposit
        self.comment = comment

    def get_id(self):
        return str(self.id)

    # 打印对象的内容
    def __repr__(self):
        return '<User %r,%r,%r,%r >' % self.name, self.phoneNumber, self.deposit, self.comment

# 书本的类
class Book(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    format = db.Column(db.String(10), unique=True)
    name = db.Column(db.String(50), unique=True)
    description = db.Column(db.String(256))
    comment = db.Column(db.String(256))

    def __init__(self, book_id=None, book_format=None, book_name=None, book_description="", comment=""):
        self.id = book_id
        self.format = book_format
        self.name = book_name
        self.description = book_description
        self.comment = comment

    def get_id(self):
        return str(self.id)

    # 打印对象的内容
    def __repr__(self):
        return '<User %r,%r,%r,%r,%r >' % (self.id, self.name, self.format, self.description, self.comment)

    # 把对象转为为本
    def to_json(self):
        return {
            'id': self.id,
            'name': self.name,
            'format': self.format,
            'description': self.description,
            'comment': self.comment,
        }


class Rental(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    rental_datetime = db.Column(db.TIMESTAMP, unique=True)
    return_datetime = db.Column(db.TIMESTAMP, unique=True)
    customer_id = db.Column(db.String(20))
    book_id = db.Column(db.String(20))
    status = db.Column(db.String(10))
    comment = db.Column(db.String(256))

    def __init__(self, rental_id=None, rental_datetime=None, return_datetime=None, customer_id="", book_id="",
                 status="", comment=""):
        self.id = rental_id
        self.rental_datetime = rental_datetime
        self.return_datetime = return_datetime
        self.customer_id = customer_id
        self.book_id = book_id
        self.status = status
        self.comment = comment

    def get_id(self):
        return str(self.id)

    # 打印对象的内容
    def __repr__(self):
        return '<User %r,%r,%r,%r >' % self.name, self.format, self.description, self.comment

# 路由
@app.route('/')
def index():
    return render_template('index.html')

# session orm对象关系模型
@app.route('/get_data')
def get_base_data():
    data = db.session.query(Book).all()
    dict1 = []
    for item in data:
        dict1.append(item.to_json())

    return jsonify({'results': dict1}) # 返回类型


@app.route('/add', methods=['POST']) # post 向服务器提交数据
def add():
    # name = request.json.get('name')

    # post_data = request.get_json()
    # print(post_data)
    parser.add_argument("format")
    parser.add_argument("name")
    parser.add_argument("description")
    parser.add_argument("comment")
    args = parser.parse_args()
    book_format = args['format']
    book_name = args['name']
    book_description = args['description']
    comment = args['comment']
    book = Book(book_format=book_format,
                  book_name=book_name,
                  book_description=book_description,
                  comment=comment)
    db.create_all()  # In case user table doesn't exists already. Else remove it. 表中不存在会创建
    db.session.add(book) # 增删改查的事物
    db.session.commit() # 提交

    # results.append({'name': name, 'index': str(uuid1())})  # uuid让index不唯一，实际开发中可以通过数据库的id来代替
    return jsonify({'message': '添加成功！'}), 200 # 返回前端成功


@app.route('/update', methods=['PUT']) # put 用请求有效载荷替换目标资源的所有当前表示。 PUT通常指定了资源的存放位置
def update():
    parser.add_argument("id", type=int)
    parser.add_argument("name", type=str)
    parser.add_argument("format", type=str)
    parser.add_argument("description", type=str)
    parser.add_argument("comment", type=str)
    args = parser.parse_args()

    item_id = args.get('id')
    new_name = args.get('name')
    new_format = args.get('format')
    new_description = args.get('description')
    new_comment = args.get('comment')
    book = db.session.query(Book).filter_by(id=item_id).first() # 查第一个

    # 将要修改的值赋给title
    if book is not None:
        book.name = new_name
        book.format = new_format
        book.description = new_description
        book.comment = new_comment

        db.session.commit()
    else:
        print("the book is None,update error")
    return jsonify({"message": "修改成功！"})


@app.route('/delete', methods=['DELETE'])
def delete():
    parser.add_argument("id", type=str, location='args')
    args = parser.parse_args()
    raw_id = args.get('id')
    book = db.session.query(Book).filter_by(id=raw_id).first()
    if book is not None:
        db.session.delete(book)
        db.session.commit()
    else:
        print("the book is None,delete error")
    return jsonify({'message': '删除成功！'})


@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
