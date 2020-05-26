import pymysql

pymysql.version_info=(1,4,6,'final',0)  # 修改myqlclient的版本
pymysql.install_as_MySQLdb()  # 通过PyMySQL来连接Mysql
