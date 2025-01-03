"""
<plugin key="Domoticz-Steam-Plugin" name="Domoticz Steam Plugin" author="Mark Heinis" version="0.0.1" wikilink="http://www.domoticz.com/wiki/plugins/plugin.html" externallink="https://github.com/galadril/Domoticz-Steam-Plugin">
    <description>
        Plugin for retrieving and updating Steam status (Online/Offline) and game name.
        
        How to fetch your SteamId?
        https://help.steampowered.com/en/faqs/view/2816-BE67-5B69-0FEC
    </description>
    <params>
        <param field="Mode1" label="SteamId" width="200px" required="true"/>
        <param field="Mode6" label="Debug" width="200px">
            <options>
                <option label="None" value="0" default="true" />
                <option label="Python Only" value="2"/>
                <option label="Basic Debugging" value="62"/>
                <option label="Basic+Messages" value="126"/>
                <option label="Connections Only" value="16"/>
                <option label="Connections+Queue" value="144"/>
                <option label="All" value="-1"/>
            </options>
        </param>
    </params>
</plugin>
"""

import Domoticz
import xml.etree.ElementTree as ET

class SteamPlugin:
    def __init__(self):
        self.steam_id = ""
        self.steam_api_host = "steamcommunity.com"
        self.steam_api_path = "/id/{}/?xml=1"
        self.STEAM_ICON_ID = "steam"
        self.connection = None
        self.initialized = False

    def onStart(self):
        Domoticz.Debugging(int(Parameters["Mode6"]))
        Domoticz.Log("onStart called")
        self.steam_id = Parameters["Mode1"]

        # Load custom icons
        self.loadIcons(Images)

        if not self.steam_id:
            Domoticz.Error("SteamId not provided")
            return

        # Initialize connection
        self.connection = Domoticz.Connection(
            Name="SteamConnection",
            Transport="TCP/IP",
            Protocol="HTTPS",
            Address=self.steam_api_host,  # Only the hostname here
            Port="443",  # Port as a string
        )
        
        self.connection.Connect()
        self.initialized = True
        Domoticz.Heartbeat(30)

    def loadIcons(self, Images):
        """Load the custom Steam icon."""
        if self.STEAM_ICON_ID in Images:
            Domoticz.Debug(f"SteamIcon ID found: {Images[self.STEAM_ICON_ID].ID}")
        else:
            Domoticz.Image("Steam-Icons.zip").Create()
            Domoticz.Log("SteamIcon added from Steam-Icons.zip")

    def onConnect(self, connection, status, description):
        """Handle the response from the connection."""
        if status != 0:
            Domoticz.Error(f"Connection failed with status {status} ({description})")
            return

        Domoticz.Log("Steam connected called")
        try:
            # Send the GET request
            connection.Send({
                "Verb": "GET",
                "URL": self.steam_api_path.format(self.steam_id),  # Path only
                "Headers": {
                    "Host": self.steam_api_host,
                    "User-Agent": "DomoticzPlugin"
                }
            })

        except Exception as e:
            Domoticz.Error(f"Error sending request: {str(e)}")

    def onMessage(self, connection, data):
        """Handle the response data."""
        try:
            response = data["Data"].decode("utf-8")
            # Parse the response XML
            tree = ET.ElementTree(ET.fromstring(response))
            root = tree.getroot()

            # Extract data from the XML
            steam_name = root.find("steamID").text
            online_state = root.find("onlineState").text
            state_message = root.find("stateMessage").text

            # Extract the game name from the stateMessage (after <br/>)
            game_name = "No Game"
            if state_message:
                game_name = state_message.split('<br/>')[1] if '<br/>' in state_message else "No Game"

            # Device name
            device_name = f"{steam_name} Status"

            # Selector levels mapping
            selector_levels = {"offline": 0, "online": 10, "in-game": 20}
            level_names = "Offline|Online|In-Game"

            # Check if the selector device exists; if not, create it
            if 1 not in Devices:
                Options = {
                    "LevelActions": "||",
                    "LevelNames": level_names,
                    "LevelOffHidden": "false",
                    "SelectorStyle": "1",
                }
                Domoticz.Device(
                    Name=device_name,
                    Unit=1,
                    TypeName="Selector Switch",
                    Options=Options,
                    Image=Images[self.STEAM_ICON_ID].ID,
                ).Create()

            # Check if the game name text device exists; if not, create it
            if 2 not in Devices:
                Domoticz.Device(
                    Name=f"{steam_name} Game Name",
                    Unit=2,
                    TypeName="Text",
                    Image=Images[self.STEAM_ICON_ID].ID,
                ).Create()

            # Determine the selector level
            level = selector_levels.get(online_state.lower(), 0)
            sValue = f"In-Game: {game_name}" if level == 20 else level_names.split("|")[level // 10]

            # Update the selector switch only if the state has changed
            if Devices[1].nValue != level or Devices[1].sValue != sValue:
                Devices[1].Update(nValue=level, sValue=f"{level}")
                Domoticz.Log(f"Updated device with nValue={level}, sValue='{level}'")

            # Update the game name text device only if the game name has changed
            if level == 20 and Devices[2].sValue != game_name:
                Devices[2].Update(nValue=0, sValue=game_name)
                Domoticz.Log(f"Updated game name text device with value '{game_name}'")

        except Exception as e:
            Domoticz.Error(f"Error processing response: {str(e)}")

    def onStop(self):
        Domoticz.Log("onStop called")

    def onHeartbeat(self):
        if not self.initialized:
            Domoticz.Log("Plugin not initialized yet")
            return

        self.connection = Domoticz.Connection(
            Name="SteamConnection",
            Transport="TCP/IP",
            Protocol="HTTPS",
            Address=self.steam_api_host,
            Port="443",
        )
        self.connection.Connect()


global _plugin
_plugin = SteamPlugin()

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

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
