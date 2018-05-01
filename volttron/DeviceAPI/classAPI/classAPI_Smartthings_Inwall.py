# -*- coding: utf-8 -*-
import time
import json
import requests

class API:

    def __init__(self,**kwargs):
        # Initialized common attributes
        self.variables = kwargs
        self.debug = True
        self.set_variable('offline_count',0)
        self.set_variable('connection_renew_interval', 6000)
        self.only_white_bulb = None

    def renewConnection(self):
        pass

    def set_variable(self,k,v):  # k=key, v=value
        self.variables[k] = v

    def get_variable(self,k):
        return self.variables.get(k, None)  # default of get_variable is none



    '''
    Attributes:
     ------------------------------------------------------------------------------------------
    label            GET          label in string
    status           GET          status
    unitTime         GET          time
    type             GET          type      
     ------------------------------------------------------------------------------------------

    '''

    '''
    API3 available methods:
    1. getDeviceStatus() GET
    2. setDeviceStatus() SET
    '''

    # ----------------------------------------------------------------------
    # getDeviceStatus(), getDeviceStatusJson(data), printDeviceStatus()
    def getDeviceStatus(self):

        getDeviceStatusResult = True
        headers = {"Authorization": self.get_variable("bearer")}
        url = str(self.get_variable("url")+self.get_variable("device"))

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
        self.set_variable('unitTime', conve_json["unitTime"])
        self.set_variable('type', str(conve_json["type"]))

    def printDeviceStatus(self):

        # now we can access the contents of the JSON like any other Python object
        print(" the current status is as follows:")
        print(" label = {}".format(self.get_variable('label')))
        print(" status = {}".format(self.get_variable('status')))
        print(" unitTime = {}".format(self.get_variable('unitTime')))
        print(" type= {}".format(self.get_variable('type')))
        print("---------------------------------------------")

    # setDeviceStatus(postmsg), isPostmsgValid(postmsg), convertPostMsg(postmsg)
    def setDeviceStatus(self, postmsg):
        setDeviceStatusResult = True
        headers = {"Authorization": self.get_variable("bearer")}
        url = str(self.get_variable("url")+self.get_variable("device"))

        if self.isPostMsgValid(postmsg) == True:  # check if the data is valid
            _data = json.dumps(self.convertPostMsg(postmsg))
            _data = _data.encode(encoding='utf_8')
            print _data
            try:
                print "sending requests put"
                r = requests.put(
                    url,
                    headers=headers, data= _data, timeout=20);
                # print "15456"
                # print r.text
                print(" {0}Agent for {1} is changing its status with {2} please wait ..."
                      .format(self.variables.get('agent_id', None), self.variables.get('model', None), postmsg))
                print(" after send a POST request: {}".format(r.status_code))
            except:
                print("ERROR: classAPI_RelaySW connection failure! @ setDeviceStatus")
                setDeviceStatusResult = False
        else:
            print("The POST message is invalid, try again\n")
        return setDeviceStatusResult

    def isPostMsgValid(self, postmsg):  # check validity of postmsg
        dataValidity = True
        # TODO algo to check whether postmsg is valid
        return dataValidity

    def convertPostMsg(self, postmsg):
        msgToDevice = {}
        if 'status' in postmsg.keys():
            msgToDevice['command'] = self.get_variable('model').capitalize() + str(postmsg['status'].lower().capitalize())
        return msgToDevice

    # ----------------------------------------------------------------------

# This main method will not be executed when this class is used as a module
def main():


    # -------------Kittchen----------------

    RelaySW = API(model='two', type='lighting', api='API_orvibo2gang', agent_id='Orvibo Light', url = 'https://graph-na02-useast1.api.smartthings.com/api/smartapps/installations/ee328927-8dc2-462e-84f3-c3b3d59ba93c/switches/', bearer = 'Bearer 80a03a69-b41f-45bb-bf0b-4acae4b63035', device='dc53a370-ed35-4228-9dc2-b0b022f28624')
    RelaySW.getDeviceStatus()
    RelaySW.setDeviceStatus({"status": "ON"})

    time.sleep(10)

    RelaySW.setDeviceStatus({"status": "OFF"})


if __name__ == "__main__": main()