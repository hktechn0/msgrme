import MySQLdb

# DB class
class msgrme_read_db:
    def __init__(self):
        self.mysql = MySQLdb.connect(HOST, USER, PASSWD, DBNAME, charset = CHARSET)
    
    def close(self):
        self.mysql.close()        
    
    # get DB info
    # ret: (passport, name, message, (deleted, public))
    def get_info(self, id = 0):
        db = self.mysql.cursor()

        q = """
SELECT `deleted`, `public`
FROM `settings`
WHERE `id`=%d""" % id
        db.execute(q)
        flags = db.fetchone()

        if flags[0] == True:
            return ("Unknown", "Unknown", "", "FLN", flags)

        q = """
SELECT `passport`, `name`, `message`, `status`
FROM `memberlist`
WHERE `id`=%d""" % id
        db.execute(q)
        info = db.fetchone()

        self.mysql.commit()
        db.close()
        
        return info

    # checkid
    # ret: if(wrong_id) -> False, else -> int(id)
    def check_id(self, id = 0):
        try:
            id = int(id)
        except:
            return False
        
        if id == 0:
            return False
        
        db = self.mysql.cursor()
        db.execute("SELECT COUNT(*) FROM memberlist")
        maxid = int(db.fetchone()[0])
        
        self.mysql.commit()
        db.close()
        
        if maxid < id:
            return False
        
        return id
