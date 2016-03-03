# -*- coding: utf-8 -*-
#
# PrivateMessaging plugin for BigBrotherBot(B3) (www.bigbrotherbot.net)
# Copyright (C) 2015 PtitBigorneau - www.ptitbigorneau.fr
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA 02110-1301 USA

__author__  = 'PtitBigorneau www.ptitbigorneau.fr'
__version__ = '1.2'


import b3
import b3.plugin
from b3 import clients
from b3.functions import getCmd

import time, threading, thread, re
import calendar
from time import gmtime, strftime


class PrivatemessagingPlugin(b3.plugin.Plugin):

    _adminPlugin = None    
    _clientminlevel = 2

    def onLoadConfig(self):

        self._clientminlevel = self.getSetting('settings', 'clientminlevel', b3.INT, self._clientminlevel)

    def onStartup(self):
        
        self._adminPlugin = self.console.getPlugin('admin')
        
        if not self._adminPlugin:

            self.error('Could not find admin plugin')
            return False

        self.registerEvent('EVT_CLIENT_AUTH', self.onClientAuth)

        if 'commands' in self.config.sections():
            for cmd in self.config.options('commands'):
                level = self.config.get('commands', cmd)
                sp = cmd.split('-')
                alias = None
                if len(sp) == 2:
                    cmd, alias = sp

                func = getCmd(self, cmd)
                if func:
                    self._adminPlugin.registerCommand(self, cmd, level, func, alias)

    def onClientAuth(self, event):

        sclient = event.client

        cursor = self.console.storage.query("""
        SELECT *
        FROM privatemessaging n 
        WHERE n.target_id = %s       
        """ % (sclient.id))

        if cursor.rowcount != 0:
            thread.start_new_thread(self.privatemessage, (event, sclient))

        cursor.close()
    
    def cmd_pmto(self, data, client, cmd=None):
        """\
        <message> - sending a private message
        """
        
        if data:
            input = self._adminPlugin.parseUserCmd(data)
            rdata = data.split(' ')

        if not data:
            client.message('!pmto <name or id client> <message>')
            return False
        
        if int(len(rdata[0]))< 2:
            client.message('need a minimum of 2 characters for the client name')
            return False

        sclient = self._adminPlugin.findClientPrompt(input[0], client)	

        if not sclient:

            if not self.console.storage.status():
                client.message('^7Cannot lookup, database apears to be ^1DOWN')
                return False

            m = re.match('^(.{1,})$', rdata[0])
        
            if not m:
                client.message('^7Invalid parameters')
                return False


            clients = self.console.clients.lookupByName(rdata[0])

            if len(clients) == 0:
                client.message('^1no players found')
                return False

            else:
                
                test = 0
                
                for c in clients:
                    
                    if test <= 10:
                        client.message('%s ^3id : ^7@%s'%(c.exactName, c.id))
                    
                    test += 1
               
                if test == 1:

                    sclient = c

                elif  test > 10:
                    client.message('^1the last 10 players connected')
                    return False

                else:
                    return False

        smessage = input[1]

        if sclient.maxLevel<self._clientminlevel:
            client.message("%s^7 has not sufficient level to receive private messages"%(sclient.exactName))
            return False

        if not smessage:
            client.message('!pmto <name or id client> <message>')
            return False

        for tclient in self.console.clients.getList():

            test2 = None

            if tclient.id == sclient.id:

                sclient.message('%s : %s'%(sclient.exactName, smessage))
                test2 = 'ok'

        if test2 == None:

            client.message('^5%s^7 is not connected, the message will be issued at her next connection'%(sclient.exactName))
            
            time_epoch = time.time() 
            time_struct = time.gmtime(time_epoch)
            date = time.strftime('%Y-%m-%d %H:%M:%S', time_struct)
            mysql_time_struct = time.strptime(date, '%Y-%m-%d %H:%M:%S') 
            mdate = calendar.timegm( mysql_time_struct)

            cursor = self.console.storage.query("""
            INSERT INTO privatemessaging
            VALUES ('%s', '%s', '%s', '%s')
            """ % (client.id, sclient.id, smessage, mdate))
            cursor.close()

    def privatemessage(self, event, sclient):

        time.sleep(30)

        cursor = self.console.storage.query("""
        SELECT *
        FROM privatemessaging
        """)
                
        while not cursor.EOF:
        
            sr = cursor.getRow()
            cid = sr['client_id']
            tid = sr['target_id']
            dmessage = sr['message']
            cdate = time.strftime('%d-%m-%Y %H:%M',time.localtime(sr['date']))

            scid= '@'+str(cid)

            if sclient.id == tid:

                dclient = self._adminPlugin.findClientPrompt(scid, sclient)
                sclient.message("^2Message : ^7%s" %(cdate))
                sclient.message("^4%s ^7: %s" %(dclient.exactName, dmessage))
                time.sleep(1)
                cursor2 = self.console.storage.query("""
                DELETE FROM privatemessaging
                WHERE date = '%s'
                """ % (sr['date']))
                cursor2.close()

            cursor.moveNext()
                    
        cursor.close()

