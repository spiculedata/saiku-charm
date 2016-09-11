import fileinput
import os
from subprocess import check_output

from charmhelpers.core.hookenv import status_set
from charmhelpers.core.host import chownr
from charmhelpers.fetch.archiveurl import ArchiveUrlFetchHandler
from charms.reactive import when_not, set_state, when

au = ArchiveUrlFetchHandler()
container = "unknown"
saiku_directory="/usr/share/saiku_ee"
saiku_url="http://www.meteorite.bi/downloads/saikuee-manual-3.8.1.zip"

@when_not('saikuanalytics-enterprise.installed')
def install_saikuanalytics_enterprise():


    if os.path.exists("/var/lib/tomcat7"):
        container="tomcat7"
    elif os.path.exists("/var/lib/tomcat6"):
        container="tomcat6"
    elif os.path.exists("/var/lib/tomcat8"):
        container="tomcat8"

    if not os.path.exists("/usr/share/"+container):
        set_state("saikuanalytics-enterprise.failed")
        status_set('blocked', 'Installation failed, container not installed correctly')
    else:
        if not os.path.exists(saiku_directory):
            os.mkdir(saiku_directory, 777)

        au.download(saiku_url, "/tmp/saikuee-manual.zip")
        check_output(["unzip", "/tmp/saikuee-manual", "-d", saiku_directory])

        check_output(["unzip", saiku_directory+"/data.zip", "-d", saiku_directory+"/data"])
        check_output(["unzip", saiku_directory+"/repository.zip", "-d", saiku_directory+"/repository"])
        check_output(["unzip", saiku_directory+"/ROOT.war", "-d", "/var/lib/"+container+"/webapps/ROOT"])
        check_output(["unzip", saiku_directory+"/saiku.war", "-d", "/var/lib/"+container+"/webapps/saiku"])

        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/saiku-beans.xml", "${WEBDAV_PASSWORD}", "passwd")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/web.xml", "${foodmart_url}", "jdbc:h2:/usr/share/saiku_ee/data/foodmart;MODE=MySQL")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/web.xml", "${earthquake_url}", "jdbc:h2:/usr/share/saiku_ee/data/earthquakes;MODE=MySQL")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/web.xml", "../../data/", "/usr/share/saiku_ee/data/")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/web.xml", "../../repository/", "/usr/share/saiku_ee/repository/")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/saiku-beans.xml", "../../repository/", "/usr/share/saiku_ee/repository/")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/saiku-beans.xml", "../../data/", "/usr/share/saiku_ee/data/")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/saiku-beans.xml", "../webapps/", "/var/lib/"+container+"/webapps/")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/applicationContext-spring-security-jdbc.properties", "../../data/", "/usr/share/saiku_ee/data")


        chownr(saiku_directory, container, container, True, True)
        set_state('saikuanalytics-enterprise.installed')
        status_set('active', 'Saiku Installed')


def replace_vars(file, old, new):
    for line in fileinput.input(file, inplace=True):
        print(line.replace(old, new), end=' ')


@when('mysql.available')
def setup(mysql):
    target = open('/var/lib/tomcat7/webapps/saiku/WEB-INF/classes/juju-datasources/mysql', "w")
    target.write("name=mysql\njdbcurl=jdbc:mysql://"+mysql.host()+":"+str(mysql.port())+"/"+mysql.database+"\nusername="+mysql.user()+"\npassword="+mysql.password()+"\ndriver=com.mysql.jdbc.Driver")

@when('pgsql.master.available')
def setup_psql(psql):
    target = open('/var/lib/tomcat7/webapps/saiku/WEB-INF/classes/juju-datasources/postgres', "w")
    target.write("name=mysql\njdbcurl=jdbc:postgresql://"+psql.master.host+":"+str(psql.master.port)+"/"+psql.master.dbname+"\nusername="+psql.master.user+"\npassword="+psql.master.password+"\ndriver=org.postgresql.Driver")

@when('jdbc.connection.available')
def setup_jdbc(jdbc):
    target = open('/var/lib/tomcat7/webapps/saiku/WEB-INF/classes/juju-datasources/drill', "w")
    target.write("name=mysql\njdbcurl="+jdbc.url+"\nusername="+jdbc.user+"\npassword="+jdbc.password+"\ndriver="+jdbc.driver)

@when('hive.ready')
def setup_psql(psql):
    target = open('/var/lib/tomcat7/webapps/saiku/WEB-INF/classes/juju-datasources/postgres', "w")
    target.write("name=mysql\njdbcurl=jdbc:postgresql://"+psql.host()+":"+psql.port()+"/"+psql.database()+"\nusername="+psql.user()+"\npassword="+psql.password()+"\ndriver=org.postgresql.Driver")

@when('hbase.ready')
def setup_psql(psql):
    target = open('/var/lib/tomcat7/webapps/saiku/WEB-INF/classes/juju-datasources/postgres', "w")
    target.write("name=mysql\njdbcurl=jdbc:postgresql://"+psql.host()+":"+psql.port()+"/"+psql.database()+"\nusername="+psql.user()+"\npassword="+psql.password()+"\ndriver=org.postgresql.Driver")
