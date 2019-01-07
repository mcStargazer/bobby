# -*- coding: utf-8 -*-

##############################################################################
# "I Spy With MySQLi" - Starring CherryPy, with co-star mysql!
##############################################################################

# REFERENCES AND PLACES TO START:
# License:   https://choosealicense.com/licenses/unlicense/ 
# cherrypy:  https://docs.cherrypy.org/en/latest/tutorials.html
# Cartoon:   https://xkcd.com/327/
#            https://www.explainxkcd.com/wiki/index.php/327:_Exploits_of_a_Mom
#            https://www.explainxkcd.com/wiki/index.php/Little_Bobby_Tables
# OWASP:     https://www.owasp.org/index.php/SQL_Injection
# Also:      http://bobby-tables.com/python
# OKCPython  https://www.meetup.com/okcpython/events/vtdhfpyzcbmb/


#
# WARNING: Do not attempt penetration testing in the wild! Only do so
#          within your own isolated environment, or ethically and
#          under contract and with clearly defined rules of engagement.
#


# import from the future
from __future__ import print_function

# import Python 2 standard modules
import json

# import third-party modules
import cherrypy
from MySQLdb import connect


##############################################################################
# Local Constants and User Function Definitions
##############################################################################


def get_config(s):

    """
    INPUTS:
        JSON configuration filename as string. Comments consisting
        of whole lines may be inserted if first character is '#'.
    OUTPUT:
        Look-up table as a dictionary
    """

    with open(s, 'r') as configuration_file:
        conf = configuration_file.readlines()

    return json.loads("".join([r for r in conf if r[0] != '#']))


#db = MySQLdb.connect("localhost","testuser","test123","TESTDB" )
def get_connection(conf):

    """
    INPUTS:
        JSON configuration file as string. Comments consisting
        of whole lines may be inserted if first character is '#'.
    OUTPUT:
        Mysql connection
    """

    # Connect to the MySQL instance
    con = connect(  host=conf["db_host"],
                    user=conf["db_user"],
                  passwd=conf["db_pass"],
                      db=conf["db_name"])
    return con


##############################################################################
# The SQLi Demonstration Application
##############################################################################

class mysqldb(object):
    
    @cherrypy.expose
    def index(self):
        """
        Page handler for the index action. It redirects to data_portal page.
        """
        raise cherrypy.HTTPRedirect("/mysqldb/data_portal")


    @cherrypy.expose
    def data_portal(self):
        """
        Page handler for data_portal.
        """
        html = """
        <html>
          <body bgcolor="#7070a0"><center>
            <h2>Student Information</h2>
            <form method="post" action="/mysqldb/get_info">
            First Name: <input size=45 type="text" name="first"/><p>
            <button type="submit">Print Info to Screen</button>
            </form>
            "Robert"<br>
            "Robert' OR 1=1); -- #"<br>            
            "'); UPDATE students SET first='Bob' WHERE last='Tables'; -- #"<br>
            "Robert'); DROP TABLE students; -- #"<br>
          </h1></center></body>
        </html>
        """

        return html


    @cherrypy.expose
    def get_info(self, first, safer=True):
        """
        The page handler for retrieval of student data
        """
        conf = get_config("./creds/db_creds.json")
        con = get_connection(conf)
        cur = con.cursor()

        if not safer:
            sql = "SELECT * FROM students WHERE (first = '%s')"
            cur.execute(sql % first)
            print ('\n' + "#"*80)
            print ("Safer: " + str(safer))
            print ("query:   " + sql)
            print ("payload: " + " "*39 + first)
            print ("result:  " + cur._last_executed)
            print ("#"*80 + '\n')
        else:
            # WARNING: The following remediation is not advertised as the
            #          best risk mitigation needed in this script, nor is
            #          it advertised as the only mitigation needed. As always
            #          you are completely responsible for securing your
            #          own applications against bad actors!
            sql = "SELECT * FROM students WHERE (first = %s)"
            cur.execute(sql, (first, ))
            print ('\n' + "#"*80)
            print ("Safer: " + str(safer))
            print ("query:   " + sql)
            print ("payload: " + " "*39 + first)
            print ("result:  " + cur._last_executed)
            print ("#"*80 + '\n')

        results = cur.fetchall()
        con.close()
        
        table = " {}, {:>8s}, {:>9s}, {}\n".format("id","first","last","info")
        for r in results:
            table += "{:3d}, {:>8s}, {:>9s}, {}\n".format(*r)
        html = """
        <html>
            <body bgcolor="#7070a0"><h3>
                <pre><h2>{}<h2></pre>
                <center><form method="post" action="data_portal">
                <button type="submit">Return to Data Portal Page</button>
                </form></center>
            </h3></body>
        </html>
        """

        return html.format(table)


    @cherrypy.expose
    def reset_db(self):
        """
        OUTPUT:
            Page handler to reset the mysql database 'student' table.
        """
        con = get_connection(get_config("./creds/db_creds.json"))
        cur = con.cursor()
            
        # re-create the Students database table
        cur.execute("DROP TABLE IF EXISTS students")
        sql = """CREATE TABLE `students` (
                 `id` INT(11) NOT NULL AUTO_INCREMENT,
                 `first` varchar(25) NOT NULL,
                 `last` varchar(25) NOT NULL,
                 `records` varchar(255) DEFAULT NULL,
                 PRIMARY KEY (id)
                 ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;"""
        cur.execute(sql)
        
        # Populate Students table with main XKCD characters mostly found
        # at https://www.explainxkcd.com/wiki/index.php/Characters
        values = [("Danish",   "Dane",      ""),
                  ("Megan",    "Archetype", ""),
                  ("Cueball",  "Archetype", ""),
                  ("Ponytail", "Alternate", ""),
                  ("Hairy",    "Alternate", ""),
                  ("Beret",    "Guy",       "surreal"),
                  ("Robert",   "Tables",    "Watch out for the mom!"),
                  ("White",    "Hat",       "often flawed/annoying"),
                  ("Black",    "Hat",       "sadistic/manipulative")]
        sql = "INSERT INTO students (first,last,records) VALUES (%s,%s,%s)"
        cur.executemany(sql, values)
        results = con.commit()
        con.close()

        html = """
        <html>
            <head>
            <body bgcolor="#7070a0"><center>
                <p><h1><em>secret administrative page</em></h1> 
                <p><h3>Database has been initialized and/or reset</h3>
                <p><h3>(Don't tell anyone the Admin is so clever...)</h3>
                <p><h1>NOT!!!</h1>
                <form method="post" action="data_portal">
                <button type="submit">Return to Data Portal Page</button>
                </form>
            </center></body>
        </html>
        """

        return html


##############################################################################
# only execute if called as a script
##############################################################################

if __name__ == '__main__':

    # configuration dictionary
    conf = {
        '/': {
            'tools.sessions.on': True
        }
    }


    # start serving the web application
    cherrypy.quickstart(mysqldb(), '/mysqldb', conf)

    ##########################################################################
    # Sample payloads. Copy the string portion into the app's text entry box
    ##########################################################################

    # data confidentiality lost through exfiltration of data
    payload0 = "Robert' OR 1=1); -- #"                  
    
    # data availability lost through destruction of table
    payload2 = "Robert'); DROP TABLE students; -- #"
    
