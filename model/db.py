import pymysql
from pymysql.cursors import DictCursor
from .static import Common
import logging
from .util import get_server_from_player_guid


PLAYER_TYPE_AUTO = 1
PLAYER_TYPE_HOLDER = 2
PLAYER_TYPE_CLIENT = 3


class DB:

    def __init__(self, host, user, password, database, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.connection = None

    def __enter__(self):
        try:
            # 创建数据库连接
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=DictCursor
            )
            logging.info(f"Successfully connected to database: {self.database}")
        except pymysql.MySQLError as e:
            logging.error(f"Failed to connect to database: {self.database}. Error: {e}")
            raise  # 将异常抛出，让外部调用方处理
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # 离开上下文时，自动关闭连接
        if self.connection:
            self.connection.close()

    def get_player_by_class(self, server, player_class, start_day, count, faction):
        assert faction in [Common.FACTION_ALLIANCE, Common.FACTION_HORDE]
        try:
            with self.connection.cursor() as cursor:
                sql = """
                    SELECT * FROM player 
                    WHERE type=1 AND available=1 AND server = %s AND class = %s AND active_day<=%s AND faction=%s 
                    ORDER BY rand() DESC LIMIT %s
                """
                cursor.execute(sql, (server, player_class, start_day, faction, count))
                result = list(cursor.fetchall())
                if len(result) < count:
                    print(player_class,faction, server, count)
                assert len(result) == count
                return result
        except pymysql.MySQLError as e:
            logging.error(f"get_player_by_class error: {e}")
            return []

    def insert_player(self, guid, name, cls, server, faction):
        assert faction in [Common.FACTION_ALLIANCE, Common.FACTION_HORDE]
        assert cls in Common.ALL_CLASS
        try:
            with self.connection.cursor() as cursor:
                sql_insert = """
                    INSERT INTO player (type, guid, server, name, class, faction) 
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql_insert, (PLAYER_TYPE_AUTO, guid, server, name, cls, faction))

                self.connection.commit()

                logging.info('insert_player done. id:%d, name:%s, server:%s'%(cursor.lastrowid, name, server ))
                return cursor.lastrowid
        except pymysql.MySQLError as e:
            logging.error(f"insert_player Error: {e}")
            self.connection.rollback()  # 出现错误时回滚
            return None
        
    #
    def get_next_name_for_server(self, server_code):
        try:
            with self.connection.cursor() as cursor:
                # Check if the server exists
                query_server = "SELECT * FROM server WHERE code = %s"
                cursor.execute(query_server, (server_code,))
                server = cursor.fetchone()
                name_index = 0
                server_id = 0

                if not server:
                    insert_server = "INSERT INTO server (code) VALUES (%s)"
                    cursor.execute(insert_server, (server_code))
                    server_id = cursor.lastrowid
                    self.connection.commit()
                    logging.info(f"new server:{server_code}")
                else:
                    name_index = server['name_index']
                    server_id = server['id']

                query_name = "SELECT * FROM name WHERE id >= %s ORDER BY id ASC LIMIT 1"
                cursor.execute(query_name, (name_index,))
                name_record = cursor.fetchone()

                if name_record:
                    next_name = name_record['name']
                    update_server_index = "UPDATE server SET name_index = %s WHERE id = %s"
                    cursor.execute(update_server_index, (name_record['id']+1, server_id))
                    self.connection.commit()
                    logging.info(f"get name for server{server_code} : {next_name}")
                    return next_name
                else:
                    logging.error(f"no name error")

        except pymysql.MySQLError as e:
            logging.error(f"get_next_name_for_server error:{e}")
            return None
        
    def get_server_name_by_code(self, code):
        try:
            with self.connection.cursor() as cursor:
                sql = 'SELECT name FROM server WHERE code=%s'
                cursor.execute(sql, (code))
                result = cursor.fetchone()
                assert result
                return result['name']
        except pymysql.MySQLError as e:
            logging.error(f"get_server_name_by_code error: {e}")
            return ''


    def insert_client(self, name, guid, faction, cls, dt):
        assert faction in [Common.FACTION_ALLIANCE, Common.FACTION_HORDE]
        server = get_server_from_player_guid(guid)
        try:
            with self.connection.cursor() as cursor:
                sql_insert = """
                    INSERT INTO player (type, name, guid, server, faction, class, active_day, available) 
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                """
                cursor.execute(sql_insert, (PLAYER_TYPE_CLIENT, name, guid, server, faction, cls, dt, 0))
                self.connection.commit()
                logging.info('insert_client done. guid:%s, id:%d'%(guid, cursor.lastrowid))
        except pymysql.MySQLError as e:
            logging.error(f"insert_client Error: {e}")


    @classmethod
    def get_player_guid(cls, id, server):
        uid = '%08x'%(int(Common.GUID_BASE, 16)+id)
        return 'Player-%s-%s'%(server, uid.upper())

    def update_player_active(self, guid, dt):
        try:
            with self.connection.cursor() as cursor:
                sql = 'UPDATE player SET active_day=%s WHERE guid=%s'
                cursor.execute(sql, (dt, guid))
                self.connection.commit()
                logging.info('update_player_active done.count:%d guid:%s, dt:%s'%(cursor.rowcount, guid, dt))
                return guid
        except pymysql.MySQLError as e:
            logging.error(f"update_player_active Error: {e}")
            self.connection.rollback()  # 出现错误时回滚
            return None
        
    

# Example usage:
if __name__ == "__main__":
    # Replace with your actual database credentials
    db = DB(host='localhost', user='root', password='', database='wcl')

    # Fetch players from server 'A1' and class 'Warrior'
    players = db.fetch_players_by_server_and_class('4781', 'Rogue')
    for player in players:
        print(player)
