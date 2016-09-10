# Overview

This charm provides [Saiku Analytics](http://meteorite.bi/products/saiku), both Enterprise and Community editions. Saiku Analytics is a flexible & lightweight web based OLAP Analysis tool that is designed to allow users to slice and dice their data using any modern web browser. Saiku Analytics will run on top of most JDBC compliant databases.

Saiku allows business users to explore complex data sources, using a familiar drag and drop interface and easy to understand business terminology, all within a browser. Select the data you are interested in, look at it from different perspectives, drill into the detail. Once you have your answer, save your results, share them, export them to Excel or PDF, all straight from the browser.

## Analyse and explore data. Wherever it is stored.

Saiku connects to a wide range of data sources allowing you to explore the data in real-time directly from the source.

Some examples are:

* Microsoft SQL Server
* Microsoft Analysis Services
* Oracle Database
* Oracle Essbase
* MySQL
* PostgreSQL
* Cloudera Impala
* Actian Vectorwise
* Amazon Redshift
* Teradata
* Vertica

## User driven dashboarding.

(Enterprise only)

Give users the ability to create their own dashboards from Saiku reports. Using the Saiku Dashboard Designer users can build and deploy their own flexible, parameter driven dashboards, without writing a single line of code. Filter reports in unison with combined filters, show the data your users want with the minimum of fuss.

## Unlock the data in your application or website.

Extend the functionality of your application with self service analytics. Allow your users to explore their data and answer their own questions. Customise Saiku so it fits seamlessly into your application or website.

## Give Saiku to everyone.

Saiku is designed to be as easy to deploy as it is to use. Saiku is 100% thin client. It works on any modern browser on PC, Mac and Tablet. Saiku can easily be integrated into existing security frameworks and is optimised to run on commodity server hardware even with large user communities. Intelligent caching reduces the performance impact on the underlying database and minimises network traffic.

# Usage

* Quickstart

How to deploy this charm:

    juju deploy tomcat
    juju deploy saikuanalytics-enterprise
    juju add-relation saikuanalytics-enterprise tomcat
    juju expose tomcat

To use Saiku Enterprise you either need a valid full license or obtain a trial license. If you would like to use a trial license you can have the charm install one automatically:

juju action do saikuanalytics-enterprise/0 gettriallicense

Once you have a license installed you can then browse to http://ip-address:8080 to configure the service.

To find out more about how to use Saiku Analytics you can view our wiki at [http://wiki.meteorite.bi]

# Configuration

Default login is admin/admin, this should be changed within the administration console once you have logged in.

The Saiku Charm has a number of helper actions to let you deploy a fully operational server programatically. These are entirely optional and you can perform the same actions manually.

* Add A Schema

To connect to a data source you need 2 things a Data Source connection and also a Schema definition that describes the table structure to the OLAP engine. To design schema you can find out more [here](http://wiki.meteorite.bi/display/SAIK/Schema).

    juju action do saiku/0 addschema name=spark content="$(cat ${MYDIR}/../var/spark_schema.xml)"

* Add A Data Source

Along with a schema you require a data source that defines the JDBC connection and the schema to use with that connection.

    juju action do saiku/0 adddatasource content="type=OLAP\nname=taxi\ndriver=mondrian.olap4j.MondrianOlap4jDriver\nlocation=jdbc:mondrian:Jdbc=jdbc:hive2://${SPARK_PRIVATE_IPADDRESS}:10000;Catalog=mondrian:///datasources/spark.xml;JdbcDrivers=org.apache.hive.jdbc.HiveDriver;\nusername=admin\npassword=admin\n"

* Add A report

You can prepopulate the Saiku repository with reports with the following action.

    juju action do saiku/0 addreport content="$(cat ${MYDIR}/../var/demo_1.saiku)" path="/homes/home:admin/demo_1.saiku"

* Add A License

If you already have a Saiku Enterprise license, you can SCP it to the server, then install the license with this action.

    juju scp "${MYDIR}/../var/license.lic" saiku/0:/tmp/license.lic
    juju action do saiku/0 addlicense path="/tmp/license.lic"

* Warm Cache

Saiku makes extensive use of caching to speed up response times especially over large and/or slow data sets. You can use this action to "warm the cache", so that users who login and run a query that can make use of the resultset this query provides will get a near instant response instead of the server having to read from the database. You can warm the cache with as many queries as you like.
 
    juju action do saiku/0 warmcache cubeconnection=taxi-mongo cubecatalog="Taxi Fares" cubeschema="Taxi Fares" cubename="Fares" query="WITH SET [~ROWS] AS {[Fares].[Payment Type].[Payment Type].Members} SELECT NON EMPTY {[Measures].[Max Tip Amount]} ON COLUMNS, NON EMPTY [~ROWS] ON ROWS FROM [Fares]"

* Get Trial License

The Juju charm allows you to download a 14 day trial license for Saiku Enterprise. Once this action has been run it will put in place the license and you should be able to login.

    juju action do saikuanalytics-enterprise/0 gettriallicense


# Contact Information

- [Main Website](http://meteorite.bi)
- [Issue Tracker](http://jira.meteorite.bi)
- [User mailing list](https://groups.google.com/a/saiku.meteorite.bi/forum/#!forum/user)
- [Saiku on Freenode IRC](http://irc.lc/freenode/%23saiku/t4nk@)
- [Saiku on Slack](http://chat.meteorite.bi)
