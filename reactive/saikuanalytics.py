import fileinput
import os
import yaml
from subprocess import check_output

from charmhelpers.core.host import chownr
from charmhelpers.fetch.archiveurl import ArchiveUrlFetchHandler
from charms.reactive import when_not, set_state, when
from charmhelpers.core import hookenv
from charmhelpers.core.hookenv import status_set, log, resource_get
from charms.layer import snap
from charms.reactive.helpers import data_changed


@when_not('saikuanalytics.installed')
def install_saikuanalytics_enterprise():


    status_set('maintenance', 'Installing saiku-enterprise snap ')
    snap.install('saiku-enterprise', channel="edge", devmode=True)
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

@when('saikuanalytics.installed')
def update_sla():
    sla = os.environ['JUJU_SLA']
    log("SLA detected:" +sla)
    data = ""
    if sla == "unsupported":
        data = "202063630746ddb796876e26b91570f3"
    elif sla == "jujuessential":
        data = "e9730e721a1b24d39d153f1bed832db5"
    elif sla == "jujustandard":
        data = "3e17f3b32b8132eb9516093acf300805"
    elif sla == "jujuadvanced":
        data = "0c046cec7cdfd176da05674208e39849"

    if not os.path.exists("/etc/saiku"):
      os.makedirs("/etc/saiku")

    slaFile = open("/etc/saiku/shash", "w")
    slaFile.write(data)
    slaFile.close()    


def update_settingsjs(varname, newvalue):
    log("updating config")
    with open("/var/snap/saiku-enterprise/current/base/webapps/ROOT/js/saiku/Settings.yaml", 'r') as stream:
        try:
            data = yaml.load(stream)
            log(data)
            data[varname] = newvalue
            with open('/var/snap/saiku-enterprise/current/base/webapps/ROOT/js/saiku/Settings.yaml', 'w') as outfile:
                yaml.dump(data, outfile, default_flow_style=False)
        except yaml.YAMLError as exc:
             log(exc)

def replace_vars(file, old, new):
    for line in fileinput.input(file, inplace=True):
        print(line.replace(old, new), end=' ')


@when('mysql.available')
def setup(mysql):
    target = open('/var/snap/saiku-enterprise/current/base/webapps/saiku/WEB-INF/classes/juju-datasources/mysql', "w")
    target.write("name=mysql\njdbcurl=jdbc:mysql://"+str(mysql.host())+":"+str(mysql.port())+"/"+str(mysql.database())+"\nusername="+str(mysql.user())+"\npassword="+str(mysql.password())+"\ndriver=com.mysql.jdbc.Driver")

@when('pgsql.master.available')
def setup_psql(psql):
    target = open('/var/snap/saiku-enterprise/current/base/webapps/saiku/WEB-INF/classes/juju-datasources/postgres', "w")
    target.write("name=mysql\njdbcurl=jdbc:postgresql://"+psql.master.host+":"+str(psql.master.port)+"/"+psql.master.dbname+"\nusername="+psql.master.user+"\npassword="+psql.master.password+"\ndriver=org.postgresql.Driver")


@when('hive.ready')
def setup_psql(psql):
    target = open('/var/snap/saiku-enterprise/current/base/webapps/saiku/WEB-INF/classes/juju-datasources/hive', "w")
    target.write("name=hive\njdbcurl=jdbc:postgresql://"+psql.host()+":"+psql.port()+"/"+psql.database()+"\nusername="+psql.user()+"\npassword="+psql.password()+"\ndriver=org.postgresql.Driver")

@when('hbase.ready')
def setup_psql(psql):
    target = open('/var/snap/saiku-enterprise/current/base/webapps/saiku/WEB-INF/classes/juju-datasources/hbase', "w")
    target.write("name=hbase\njdbcurl=jdbc:postgresql://"+psql.host()+":"+psql.port()+"/"+psql.database()+"\nusername="+psql.user()+"\npassword="+psql.password()+"\ndriver=org.postgresql.Driver")

@when('jdbc.available')
def setup_drill(jdbc):
    target = open('/var/snap/saiku-enterprise/current/base/webapps/saiku/WEB-INF/classes/juju-datasources/'+jdbc.host(), "w")
    target.write("name="+jdbc.host()+"\njdbcurl="+jdbc.url()+"\ndriver="+jdbc.driver())

