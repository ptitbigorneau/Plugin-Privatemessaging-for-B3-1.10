# privatemessaging plugin
# Plugin for B3 (www.bigbrotherbot.net)
# www.ptitbigorneau.fr

privatemessaging plugin (v1.2) for B3

Requirements
------------

* BigBortherBot(3) >= version 1.10

Installation:
-------------

1. Copy the 'privatemessaging' folder into 'b3/extplugins' and 'privatemessaging.ini' file into '/b3/extplugins/conf'.

2. Open your B3.ini or b3.xml file (default in b3/conf) and add the next line in the [plugins] section of the file:
    for b3.xml
        <plugin name="privatemessaging" config="@b3/extplugins/conf/privatemessaging.ini"/>
    for b3.ini
        privatemessaging: @b3/extplugins/conf/privatemessaging.ini

4. Run the privatemessaging SQL script (privatemessaging.sql) on your B3 database