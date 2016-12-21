# coding: utf-8
__author__ = 'liufei'
import sqlite3
import json

class SqliteHelper:
    '''
    数据库的配置
    '''
    DB_CONFIG = {
        'dbType': 'sqlite',#sqlite,mysql,mongodb
        'dbPath': 'data/ranker.db',#这个仅仅对sqlite有效
        'dbUser': '',#用户名
        'dbPass': '',#密码
        'dbName': ''#数据库名称
    }
    table_customer = "customer"
    table_ranker = "ranker"
    table_tasks = "tasks"

    def __init__(self):
        '''
        建立数据库的链接
        '''
        self.database = sqlite3.connect(self.DB_CONFIG['dbPath'], check_same_thread=False)
        self.cursor = self.database.cursor()

        #创建表结构
        self.createTable_customer()
        self.createTable_ranker()
        self.createTable_tasks()

    def __del__(self):
        try:
            self.close()
        except:
            pass

    def compress(self):
        '''
        数据库进行压缩
        '''
        self.database.execute('VACUUM')

    def createTable_customer(self):
        # name - 用户名字
        # customer_info - 用户详细信息
        # vaild_data - 订单截止日期
        # updatetime - 数据更新时间
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
        # customerid - 用户订单id
        # keyword - 需要操作的关键字
        # searcher -  搜索引擎: 0-百度; 1-神马; 2-搜狗
        # searcher - 执行平台: 0-h5; 1-web
        # runway - 执行操作方式: 0-刷指数+刷权重 1-只刷指数
        # targeturl_keyword - 目标页面URL中包含的关键字, 以此作为匹配目标页面的标志
        # target_runtimes - 指数点击次数
        # clicked_times - 当日已经点击次数
        # updatetime - 记录更新时间
        # status - 状态,0-无效;1-有效

        sql = '''
                create TABLE IF NOT EXISTS %s
                (
                    id INTEGER PRIMARY KEY,
                    customerid CHAR(10) NOT NULL,
                    keyword VARCHAR(16) NOT NULL,
                    searcher INTEGER NOT NULL DEFAULT 0,
                    platform INTEGER NOT NULL DEFAULT 0,
                    runway INTEGER NOT NULL,
                    targeturl_keyword CHAR(20) NOT NULL DEFAULT "",
                    target_runtimes INTEGER NOT NULL DEFAULT 0,
                    updatetime TimeStamp NOT NULL DEFAULT (datetime('now','localtime')),
                    status CHAR(1) NOT NULL DEFAULT 1
                )
               ''' % self.table_ranker
        self.cursor.execute(sql)
        self.database.commit()

    def createTable_tasks(self):
        # ranker_id -
        # clicked_times - 当日已经点击次数
        # updatetime - 记录更新时间

        sql = '''
                create TABLE IF NOT EXISTS %s
                (
                    id INTEGER PRIMARY KEY,
                    ranker_id INTEGER NOT NULL,
                    clicked_times INTEGER NOT NULL DEFAULT 0,
                    updatetime TimeStamp NOT NULL DEFAULT (datetime('now','localtime'))
                )
               ''' % self.table_tasks
        self.cursor.execute(sql)
        self.database.commit()

    def insert_customer(self, value):
        customer = [value['name'], value['customer_info'], value['vaild_date']]
        self.cursor.execute("INSERT INTO %s (name, customer_info, vaild_date)VALUES (?,?,?)" % self.table_customer, customer)

    def insert_ranker(self, value):
        ranker = [value['customerid'], value['keyword'], value['searcher'], value['platform'], value['runway'], value['targeturl_keyword'], value['target_runtimes']]
        self.cursor.execute("INSERT INTO %s (customerid, keyword, searcher, platform, runway, targeturl_keyword, target_runtimes) VALUES (?,?,?,?,?,?,?)" % self.table_ranker, ranker)

    def insert_tasks(self, ranker_id):
        self.cursor.execute("INSERT INTO %s (ranker_id) VALUES (%d)" % (self.table_tasks, ranker_id))
        self.database.commit()

    def update_clicked_times(self, id):
        sql = 'UPDATE %s SET %s WHERE %s' % (self.table_tasks, "clicked_times = clicked_times + 1, updatetime = datetime('now','localtime')", "date(updatetime) = date('now','localtime') and ranker_id = %d" % id)
        self.cursor.execute(sql)
        self.database.commit()

    def select_today_tasks(self):
        sql = '''
        select r.id, searcher, platform, runway, keyword, targeturl_keyword, (target_runtimes - clicked_times) times
        from ranker r, customer c, tasks t
        where c.id = r.customerid and r.id= t.ranker_id and c.vaild_date >= date('now','localtime') and times > 0
        and r.status = 1 and date(t.updatetime) = date('now','localtime')
        '''
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        taskList, index = [], 1
        for t in result:
            task, value = {}, {}
            task['T%d' % index] = value
            value['taskid'] = t[0]
            value['searcher'] = t[1]
            value['drvierType'] = t[2]
            value['func'] = t[3]
            value['keyword'] = t[4]
            value['targeturl_keyword'] = t[5]
            value['runtime'] = t[6]
            index += 1
            taskList.append(task)
        return json.dumps(taskList)

    def is_exist_task_record(self, ranker_id):
        sql = 'select id from %s where ranker_id = %d and date(updatetime) = date("now", "localtime")' % (self.table_tasks, ranker_id)
        self.cursor.execute(sql)
        for row in self.cursor.fetchall():
            for r in row:
                return r

    def select_runtime(self, ranker_id):
        sql = 'select target_runtimes - clicked_times from %s r, %s t where r.id = t.ranker_id  and date(t.updatetime) = date("now","localtime") and r.id = %d' % (self.table_ranker, self.table_tasks, ranker_id)
        self.cursor.execute(sql)
        for row in self.cursor.fetchall():
            for r in row:
                return r

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

    #添加任务数据
    content = {
        'customerid': 2,
        'keyword': u'中青旅遨游网',
        'searcher': 0,
        'platform': '0',
        'runway': 1,
        'targeturl_keyword': u'遨游网',
        'target_runtimes': 400
    }
    sh.insert_ranker(content)
    sh.commit()

    #添加执行情况数据
    sh.insert_tasks(1)
    sh.commit()
    '''
    # 测试is_exist_task_record()
    print sh.is_exist_task_record(3)

    # 测试update_clicked_times()
    sh.update_clicked_times(1)

    # 测试select_runtime()
    print sh.select_runtime(1)

    # 测试select_today_tasks()
    print sh.select_today_tasks()