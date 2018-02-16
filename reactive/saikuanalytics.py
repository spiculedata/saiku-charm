import fileinput
import os
from subprocess import check_output

from charmhelpers.core.host import chownr
from charmhelpers.fetch.archiveurl import ArchiveUrlFetchHandler
from charms.reactive import when_not, set_state, when
from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import status_set, log, resource_get
from charms.layer import snap


@when_not('saikuanalytics.installed')
def install_saikuanalytics_enterprise():


    channel = config ('channel')
    status_set('maintenance', 'Installing saiku-enterprise snap ')
    snap.install('pentaho-biserver-spicule', channel="edge", devmode=True)
    hookenv.open_port(8080)
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

    jsonFile = open("/var/lib/"+container+"/webapps/ROOT/js/saiku/Settings.js", "w+")
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
