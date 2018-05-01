# -*- coding: utf-8 -*-
'''
Copyright (c) 2016, Virginia Tech
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
 following conditions are met:
1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following
disclaimer.
2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be
interpreted as representing official policies, either expressed or implied, of the FreeBSD Project.

This material was prepared as an account of work sponsored by an agency of the United States Government. Neither the
United States Government nor the United States Department of Energy, nor Virginia Tech, nor any of their employees,
nor any jurisdiction or organization that has cooperated in the development of these materials, makes any warranty,
express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness or
any information, apparatus, product, software, or process disclosed, or represents that its use would not infringe
privately owned rights.

Reference herein to any specific commercial product, process, or service by trade name, trademark, manufacturer, or
otherwise does not necessarily constitute or imply its endorsement, recommendation, favoring by the United States
Government or any agency thereof, or Virginia Tech - Advanced Research Institute. The views and opinions of authors
expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.

VIRGINIA TECH – ADVANCED RESEARCH INSTITUTE
under Contract DE-EE0006352

#__author__ = "BEMOSS Team"
#__credits__ = ""
#__version__ = "2.0"
#__maintainer__ = "BEMOSS Team"
#__email__ = "aribemoss@gmail.com"
#__website__ = "www.bemoss.org"
#__created__ = "2014-09-12 12:04:50"
#__lastUpdated__ = "2016-03-14 11:23:33"
'''

import time
import json
import requests

class API:

    def __init__(self,**kwargs):

        self.variables = kwargs
        self.debug = True
        self.set_variable('offline_count',0)
        self.set_variable('connection_renew_interval', 6000)
        self.only_white_bulb = None

    def renewConnection(self):
        pass

    def set_variable(self,k,v):
        self.variables[k] = v

    def get_variable(self,k):
        return self.variables.get(k, None)


    '''
    Attributes:
     ------------------------------------------------------------------------------------------
    label            GET          label in string
    unitTime         GET          Hue light effect 'none' or 'colorloop'
    type             GET          type
    status           GET          status
    power            GET          power
     ------------------------------------------------------------------------------------------

    '''

    '''
    API3 available methods:
    1. getDeviceStatus() GET
    '''    

    # ----------------------------------------------------------------------
    # getDeviceStatus(), getDeviceStatusJson(data), printDeviceStatus()
    def getDeviceStatus(self):

        getDeviceStatusResult = True

        headers = {"Authorization": self.get_variable("bearer")}
        url = str(self.get_variable("url")+self.get_variable("device"))
        print(url)
        try:
            r = requests.get(url,
                             headers=headers, timeout=20);
            print("{0} Agent is querying its current status (status:{1}) please wait ...".format(self.get_variable('agent_id'), r.status_code))
            format(self.variables.get('agent_id', None), str(r.status_code))
            print r.text
            if r.status_code == 200:
                getDeviceStatusResult = False

                self.getDeviceStatusJson(r.text)
                if self.debug is True:
                    self.printDeviceStatus()
            else:
                print (" Received an error from server, cannot retrieve results")
                getDeviceStatusResult = False

            if getDeviceStatusResult==True:
                self.set_variable('offline_count', 0)
            else:
                self.set_variable('offline_count', self.get_variable('offline_count')+1)
        except Exception as er:
            print er
            print('ERROR: classAPI_PhilipsHue failed to getDeviceStatus')
            self.set_variable('offline_count',self.get_variable('offline_count')+1)

    def getDeviceStatusJson(self, data):

        conve_json = json.loads(data)
        self.set_variable('label', str(conve_json["label"]))
        self.set_variable('status', str(conve_json["status"]).upper())
        self.set_variable('power', str(conve_json["power"]))
        self.set_variable('unitTime', conve_json["unitTime"])
        self.set_variable('type', str(conve_json["type"]))

    def printDeviceStatus(self):


        print(" the current status is as follows:")
        print(" label = {}".format(self.get_variable('label')))
        print(" status = {}".format(self.get_variable('status')))
        print(" power = {}".format(self.get_variable('power')))
        print(" unitTime = {}".format(self.get_variable('unitTime')))
        print(" type= {}".format(self.get_variable('type')))
        print("---------------------------------------------")


    def setDeviceStatus(self, postmsg):
        setDeviceStatusResult = True
        headers = {"Authorization": self.get_variable("bearer")}
        url = str(self.get_variable("url")+self.get_variable("device"))


        if self.isPostMsgValid(postmsg) == True:
            _data = json.dumps(self.convertPostMsg(postmsg))
            _data = _data.encode(encoding='utf_8')
            print _data
            try:
                print "sending requests put"
                r = requests.put(
                    url,
                    headers=headers, data= _data, timeout=20);

                print(" {0}Agent for {1} is changing its status with {2} please wait ..."
                      .format(self.variables.get('agent_id', None), self.variables.get('model', None), postmsg))
                print(" after send a POST request: {}".format(r.status_code))
            except:
                print("ERROR: classAPI_RelaySW connection failure! @ setDeviceStatus")
                setDeviceStatusResult = False
        else:
            print("The POST message is invalid, try again\n")
        return setDeviceStatusResult

    def isPostMsgValid(self, postmsg):
        dataValidity = True
        # TODO algo to check whether postmsg is valid
        return dataValidity

    def convertPostMsg(self, postmsg):
        msgToDevice = {}
        if 'status' in postmsg.keys():
            msgToDevice['command'] = str(postmsg['status'].lower())
        return msgToDevice


def main():


    # -------------Kittchen----------------
    RelaySW = API(model='RelaySW', type='tv', api='API3', agent_id='RelaySWAgent',url = 'https://graph-na02-useast1.api.smartthings.com/api/smartapps/installations/ee328927-8dc2-462e-84f3-c3b3d59ba93c/switches/', bearer='Bearer 80a03a69-b41f-45bb-bf0b-4acae4b63035', device='a8b5d221-f1e1-4c22-9ded-1111e4e5b8ea')
    RelaySW.getDeviceStatus()

    RelaySW.setDeviceStatus({"status": "on"})

    time.sleep(10)

    RelaySW.setDeviceStatus({"status": "off"})

    time.sleep(10)

    RelaySW.setDeviceStatus({"status": "on"})


if __name__ == "__main__": main()