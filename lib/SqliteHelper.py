# coding: utf-8
__author__ = 'liufei'
from lib.SqlHelper import SqlHelper
import sqlite3

class SqliteHelper(SqlHelper):
    '''
    数据库的配置
    '''
    DB_CONFIG = {
        'dbType':'sqlite',#sqlite,mysql,mongodb
        'dbPath':'../data/ranker.db',#这个仅仅对sqlite有效
        'dbUser':'',#用户名
        'dbPass':'',#密码
        'dbName':''#数据库名称
    }
    table_customer = "customer"
    table_ranker = "ranker"

    def __init__(self):
        '''
        建立数据库的链接
        '''
        self.database = sqlite3.connect(self.DB_CONFIG['dbPath'], check_same_thread=False)
        self.cursor = self.database.cursor()

        #创建表结构
        self.createTable_customer()
        self.createTable_ranker()

    def compress(self):
        '''
        数据库进行压缩
        '''
        self.database.execute('VACUUM')

    def createTable_customer(self):
        sql = '''
                create TABLE IF NOT EXISTS %s
                (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(10) NOT NULL,
                    customer_info VARCHAR(40) NOT NULL,
                    vaild_date date NOT NULL DEFAULT (date('now','localtime')),
                    updatetime TimeStamp NOT NULL DEFAULT (datetime('now','localtime'))
                )
               ''' % self.table_customer
        self.cursor.execute(sql)
        self.database.commit()

    def createTable_ranker(self):
        sql = '''
                create TABLE IF NOT EXISTS %s
                (
                    id INTEGER PRIMARY KEY,
                    customerid CHAR(10) NOT NULL,
                    keyword VARCHAR(16) NOT NULL,
                    platform CHAR(6) NOT NULL, runway INTEGER NOT NULL,
                    target_runtimes INTEGER NOT NULL DEFAULT 0, clicked_times INTEGER NOT NULL DEFAULT 0,
                    updatetime TimeStamp NOT NULL DEFAULT (datetime('now','localtime'))
                )
               ''' % self.table_ranker
        self.cursor.execute(sql)
        self.database.commit()

    def insert_customer(self, value):
        customer = [value['name'], value['customer_info'], value['vaild_date']]
        self.cursor.execute("INSERT INTO %s (name, customer_info, vaild_date)VALUES (?,?,?)" % self.table_customer, customer)

    def insert_ranker(self, value):
        ranker = [value['customerid'], value['keyword'], value['platform'], value['runway'], value['target_runtimes']]
        self.cursor.execute("INSERT INTO %s (customerid, keyword, platform, runway, target_runtimes) VALUES (?,?,?,?,?)" % self.table_ranker, ranker)

    def select_today_tasks(self):
        sql = '''
        select keyword, platform, runway, target_runtimes, clicked_times
        from ranker r left join customer c on r.customerid = c.id
        where vaild_date >= date('now','localtime')
        '''
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        return result

    def update(self,tableName, condition, value):
        self.cursor.execute('UPDATE %s %s'%(tableName, condition), value)
        self.database.commit()

    def delete(self, tableName, condition):
        deleCommand = 'DELETE FROM %s WHERE %s' % (tableName, condition)
        # print deleCommand
        self.cursor.execute(deleCommand)
        self.commit()

    def commit(self):
        self.database.commit()

    def close(self):
        self.cursor.close()
        self.database.close()

if __name__ == "__main__":
    sh = SqliteHelper()
    ''' #添加订单数据
    content = {
        'name': 'LiuFei',
        "customer_info": u"这是刘飞测试程序使用的客户信息字段内容",
        "vaild_date": "2017-04-04"
    }
    sh.insert_customer(content)
    sh.commit()
    '''

    ''' #添加任务数据
    content = {
        'customerid': 2,
        'keyword': u'中青旅遨游网',
        'platform': 'h5',
        'runway': 1,
        'target_runtimes': 200
    }
    sh.insert_ranker(content)
    sh.commit()
    '''

    #查询当日任务
    print sh.select_today_tasks()
