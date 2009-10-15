import MySQLdb

# DB Method
class msgrme_db:
    def __init__(self, host, user, passwd, dbname, charset):
        self.mysql = MySQLdb.connect(host, user, passwd, dbname, charset = charset)

    def close(self):
        self.mysql.close()

    def to_offline(self):
        #self.mysql.query('UPDATE memberlist SET name="Unknown", message="", status="FLN"')
        self.mysql.query('UPDATE settings SET deleted=TRUE, public=FALSE')
        self.mysql.commit()

    def setup(self):
        db = self.mysql.cursor()
        q = '''
CREATE TABLE `memberlist` (
`id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY ,
`passport` VARCHAR(255) NOT NULL ,
`name` TEXT NOT NULL ,
`message` TEXT NULL ,
`status` VARCHAR(3) NOT NULL ,
UNIQUE (`passport`)
) ENGINE = InnoDB'''
        db.execute(q)

        q = '''
CREATE TABLE `settings` (
`id` INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY ,
`deleted` BOOL NOT NULL ,
`public` BOOL NOT NULL
) ENGINE = InnoDB'''
        db.execute(q)

        self.mysql.commit()
        db.close()

    def add_member(self, contact):
        db = self.mysql.cursor()
        q = 'INSERT INTO memberlist VALUES(NULL,"%s","%s","%s","%s")' % (
            self.mysql.escape_string(contact.account),
            self.mysql.escape_string(contact.display_name),
            self.mysql.escape_string(contact.personal_message),
            contact.presence)
        db.execute(q)
        q = 'INSERT INTO settings VALUES(NULL, FALSE, FALSE)'
        db.execute(q)
        self.mysql.commit()
        db.close()

    def update_member(self, contact):
        disp_name = contact.display_name
        message = contact.personal_message
        presence = contact.presence
        
        db = self.mysql.cursor()
        q = '''
UPDATE memberlist
SET name="%s", message="%s", status="%s"
WHERE passport="%s"''' % (
            self.mysql.escape_string(disp_name),
            self.mysql.escape_string(message),
            presence,
            self.mysql.escape_string(contact.account))

        db.execute(q) 
        self.mysql.commit()
        db.close()

    def check_member(self, contact):
        db = self.mysql.cursor()
        q = 'SELECT * FROM memberlist WHERE passport="%s"' % (
            self.mysql.escape_string(contact.account))
        db.execute(q)
        q = db.fetchone()
        
        add_id = 0
        if q == ():
            self.add_member(contact)
            add_id = self.get_id(contact)
            
        self.mysql.commit()
        db.close()
        return add_id

    def get_id(self, contact):
        db = self.mysql.cursor()
        q = 'SELECT id FROM memberlist WHERE passport="%s"' % (
            self.mysql.escape_string(contact.account))
        db.execute(q)
        q = db.fetchone()
        self.mysql.commit()
        db.close()
        return int(q[0])

    def set_deleted(self, id, flag = True):
        db = self.mysql.cursor()
        q = 'UPDATE settings SET deleted=%s WHERE id=%d' % (flag, int(id))
        db.execute(q)
        self.mysql.commit()
        db.close()
