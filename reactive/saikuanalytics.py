import fileinput
import os
from subprocess import check_output

from charmhelpers.core.hookenv import status_set
from charmhelpers.core.host import chownr
from charmhelpers.fetch.archiveurl import ArchiveUrlFetchHandler
from charms.reactive import when_not, set_state, when
from charmhelpers.core.hookenv import status_set, log, resource_get

container = "unknown"
saiku_directory="/usr/share/saiku_ee"
saiku = ''
path = ''

@when_not('saikuanalytics.installed')
def install_saikuanalytics_enterprise():


    if os.path.exists("/var/lib/tomcat7"):
        container="tomcat7"
    elif os.path.exists("/var/lib/tomcat6"):
        container="tomcat6"
    elif os.path.exists("/var/lib/tomcat8"):
        container="tomcat8"

    if not os.path.exists("/usr/share/"+container):
        set_state("saikuanalytics.failed")
        status_set('blocked', 'Installation failed, container not installed correctly')
    else:
        if not os.path.exists(saiku_directory):
            os.mkdir(saiku_directory, 754)

        if(hookenv.config('version')=='enterprise'):
            saiku = resource_get("saiku_ee")
            path = 'saiku_ee'
        else:
            saiku = resource_get("saiku_ce")
            path = 'saiku_ce'

        check_output(["unzip", saiku, "-d", saiku_directory])

        check_output(["unzip", saiku_directory+"/data.zip", "-d", saiku_directory+"/data"])
        check_output(["unzip", saiku_directory+"/repository.zip", "-d", saiku_directory+"/repository"])
        check_output(["unzip", saiku_directory+"/ROOT.war", "-d", "/var/lib/"+container+"/webapps/ROOT"])
        check_output(["unzip", saiku_directory+"/saiku.war", "-d", "/var/lib/"+container+"/webapps/saiku"])

        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/saiku-beans.xml", "${WEBDAV_PASSWORD}", "passwd")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/web.xml", "${foodmart_url}", "jdbc:h2:/usr/share/saiku_ee/data/foodmart;MODE=MySQL")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/web.xml", "${earthquake_url}", "jdbc:h2:/usr/share/saiku_ee/data/earthquakes;MODE=MySQL")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/web.xml", "../../data/", "/usr/share/"+path+"/data/")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/web.xml", "../../repository/", "/usr/share/"+path+"/repository/")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/saiku-beans.xml", "../../repository/", "/usr/share/"+path+"/repository/")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/saiku-beans.xml", "../../data", "/usr/share/"+path+"/data/")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/saiku-beans.xml", "../webapps/", "/var/lib/"+container+"/webapps/")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/saiku-beans.properties", "../../data", "/usr/share/"+path+"/data")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/saiku-beans.properties", "../../repository", "/usr/share/"+path+"/repository")

        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/applicationContext-spring-security-jdbc.properties", "../../data/", "/usr/share/"+path+"/data")
        replace_vars("/var/lib/"+container+"/webapps/saiku/WEB-INF/applicationContext-spring-security.xml", "${AUTH_TYPE}", "jdbc")


        chownr(saiku_directory, container, container, True, True)
        set_state('saikuanalytics.installed')
        status_set('active', 'Saiku Installed')

@when('saikuanalytics.installed')
def check_config():
    if data_changed('dimension_prefetch', hookenv.config('dimension_prefetch')):
        update_settingsjs('DIMENSION_PREFETCH', hookenv.config('dimension_prefetch'))
    if data_changed('DIMENSION_SHOW_ALL', hookenv.config('dimension_show_all')):
        update_settingsjs('dimension_show_all', hookenv.config('dimension_show_all'))
    if data_changed('dimension_hide_hierarchy', hookenv.config('dimension_hide_hierarchy')):
        update_settingsjs('DIMENSION_HIDE_HIERARCHY', hookenv.config('dimension_hide_hierarchy'))
    if data_changed('i18n_locale', hookenv.config('i18n_locale')):
        update_settingsjs('I18N_LOCALE', hookenv.config('i18n_locale'))
    if data_changed('table_lazy_load', hookenv.config('table_lazy_load')):
        update_settingsjs('TABLE_LAZY', hookenv.config('table_lazy_load'))
    if data_changed('table_lazy_size', hookenv.config('table_lazy_size')):
        update_settingsjs('TABLE_LAZY_SIZE', hookenv.config('table_lazy_size'))
    if data_changed('cellset_formatter', hookenv.config('cellset_formatter')):
        update_settingsjs('CELLSET_FORMATTER', hookenv.config('cellset_formatter'))
    if data_changed('result_limit', hookenv.config('result_limit')):
        update_settingsjs('RESULT_LIMIT', hookenv.config('result_limit'))
    if data_changed('members_from_result', hookenv.config('members_from_result')):
        update_settingsjs('MEMBERS_FROM_RESULT', hookenv.config('members_from_result'))
    if data_changed('members_limit', hookenv.config('members_limit')):
        update_settingsjs('MEMBERS_LIMIT', hookenv.config('members_limit'))
    if data_changed('allow_parameters', hookenv.config('allow_parameters')):
        update_settingsjs('ALLOW_PARAMETERS', hookenv.config('allow_parameters'))
    if data_changed('default_view_state', hookenv.config('default_view_state')):
        update_settingsjs('DEFAULT_VIEW_STATE', hookenv.config('default_view_state'))
    if data_changed('evaluation_panel_login', hookenv.config('evaluation_panel_login')):
        update_settingsjs('EVALUATION_PANEL_LOGIN', hookenv.config('evaluation_panel_login'))
    if data_changed('show_refresh_nonadmin', hookenv.config('show_refresh_nonadmin')):
        update_settingsjs('SHOW_REFRESH_NONADMIN', hookenv.config('show_refresh_nonadmin'))
    if data_changed('hide_empty_rows', hookenv.config('hide_empty_rows')):
        update_settingsjs('HIDE_EMPTY_ROWS', hookenv.config('hide_empty_rows'))

def update_settingsjs(varname, newvalue):
    jsonFile = open("/var/lib/"+container+"/webapps/ROOT/js/saiku/Settings.js", "r")
    data = json.load(jsonFile)
    jsonFile.close()

    data[varname] = newvalue

    jsonFile = open("/var/lib/"+container+"/webapps/ROOT/js/saiku/Settings.js"", "w+")
    jsonFile.write(json.dumps(data))
    jsonFile.close()

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
