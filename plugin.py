<plugin key="SensairS8" name="Sensair S8 CO sensor" author="artbern" version="1.0.0" wikilink="https://github.com/ArtBern/Domoticz-SensairS8-plugin" externallink="https://github.com/ArtBern/Domoticz-SensairS8-plugin">
    <description>
        <h2>Sensair S8 CO2 sensor</h2><br/>
        Read PPM values from Sensair S8 CO2 sensor
        <h3>Devices</h3>
        <ul style="list-style-type:square">
            <li>Device Type - What it does...</li>
        </ul>
        <h3>Configuration</h3>
        Configuration options...
    </description>
    <params>
    </params>
</plugin>
"""
import Domoticz
import time
import serial

class BasePlugin:
    enabled = False
    def __init__(self):
        var port = "/dev/ttyS0"
        var baudrate = 9600
        var timeout = .5
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        self.ser.flushInput()        

    def onStart(self):
        Domoticz.Log("onStart called")
        if Parameters["Mode6"] == "Debug":
            Domoticz.Debugging(1)

        if (len(Devices) == 0):
            Domoticz.Device(Name="Sensair S8", Unit=1, TypeName="Air Quality", Used=1).Create()

        Domoticz.Debug("Device created.")
        DumpConfigToLog()


    def onStop(self):
        Domoticz.Log("onStop called")

    def onConnect(self, Connection, Status, Description):
        Domoticz.Log("onConnect called")

    def onMessage(self, Connection, Data):
        Domoticz.Log("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Log("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Log("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Log("onDisconnect called")

    def onHeartbeat(self):
        Domoticz.Log("onHeartbeat called")
        
        try:
            self.ser.flushInput()
            self.ser.write(b"\xFE\x44\x00\x08\x02\x9F\x25")
            time.sleep(1)
            response = self.ser.read(7)

            high = response[3]
            low = response[4]
            co2 = (high*256) + low
            UpdateDevice(1, co2, str(co2), 100)
        except Exception as e:
            co2 = None
            print(e)        

        
def UpdateDevice(Unit, nValue, sValue, batterylevel):
    # Make sure that the Domoticz device still exists (they can be deleted) before updating it 
    if (Unit in Devices):
        if (Devices[Unit].nValue != nValue) or (Devices[Unit].sValue != sValue):
            Devices[Unit].Update(nValue, str(sValue),BatteryLevel=batterylevel)
            Domoticz.Debug("Update "+str(nValue)+":'"+str(sValue)+"' ("+Devices[Unit].Name+")")

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

    # Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return
