import os
import mysql.connector

# 连接数据库
cnx = mysql.connector.connect(
    host="localhost",
    user="root",
    password=os.environ["DB_PASSWORD"],
    database="card"
)

cursor = cnx.cursor()

# 执行SQL语句
try:
    # 添加工艺特点字段
    cursor.execute("ALTER TABLE `古代精品灯具` ADD COLUMN `工艺特点` TEXT DEFAULT NULL;")
    print("添加工艺特点字段成功")
    
    # 添加历史背景字段
    cursor.execute("ALTER TABLE `古代精品灯具` ADD COLUMN `历史背景` TEXT DEFAULT NULL;")
    print("添加历史背景字段成功")
    
    cnx.commit()
    print("数据库更新成功")
except Exception as e:
    print(f"错误: {e}")
    cnx.rollback()
finally:
    cursor.close()
    cnx.close()
