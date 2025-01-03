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
import requests
import xml.etree.ElementTree as ET

class SteamPlugin:
    def __init__(self):
        self.steam_id = ""
        self.steam_api_url = "https://steamcommunity.com/id/{}/?xml=1"
        self.initialized = False
        self.STEAM_ICON_ID = "steam"
    
    def onStart(self):
        Domoticz.Debugging(int(Parameters["Mode6"]))
        Domoticz.Log("SteamPlugin: onStart called")
        self.steam_id = Parameters["Mode1"]
        
        # Load custom icons
        self.loadIcons(Images)
        
        if not self.steam_id:
            Domoticz.Error("SteamPlugin: SteamId not provided")
            return
        
        # Fetch API details and initialize
        if self.fetchSteamDetails():
            self.initialized = True
            Domoticz.Heartbeat(30)
        else:
            Domoticz.Error("SteamPlugin: Failed to initialize. Could not fetch Steam details.")
            
    def loadIcons(self, Images):
        """Load the custom Steam icon."""
        if self.STEAM_ICON_ID in Images:
            Domoticz.Debug(f"SteamIcon ID found: {Images[self.STEAM_ICON_ID].ID}")
        else:
            Domoticz.Image("Steam-Icons.zip").Create()
            Domoticz.Log("SteamPlugin: SteamIcon added from Steam-Icons.zip")
        Domoticz.Log(f"Available icons in Images: {list(Images.keys())}") 

    def fetchSteamDetails(self):
        """Fetch Steam API details, create or update a selector switch device for Steam status and a text device for the game name."""
        url = self.steam_api_url.format(self.steam_id)
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            # Parse the XML
            tree = ET.ElementTree(ET.fromstring(response.content))
            root = tree.getroot()
            
            # Extract data from the XML
            steam_name = root.find("steamID").text
            online_state = root.find("onlineState").text
            state_message = root.find("stateMessage").text
            
            # Log the parsed values
            Domoticz.Log(f"SteamPlugin: Extracted steam_name: {steam_name}")
            Domoticz.Log(f"SteamPlugin: Extracted online_state: {online_state}")
            Domoticz.Log(f"SteamPlugin: Extracted state_message: {state_message}")
            
            # Extract the game name from the stateMessage (after <br/>)
            game_name = "No Game"
            if state_message:
                game_name = state_message.split('<br/>')[1] if '<br/>' in state_message else "No Game"
            Domoticz.Log(f"SteamPlugin: Extracted game_name: {game_name}")
            
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
                    Image=Images[self.STEAM_ICON_ID].ID,  # Use the custom Steam icon
                ).Create()
                Domoticz.Log(f"SteamPlugin: Created selector switch device '{device_name}'")
            
            # Check if the game name text device exists; if not, create it
            if 2 not in Devices:
                Domoticz.Device(
                    Name=f"{steam_name} Game Name",
                    Unit=2,
                    TypeName="Text",
                    Image=Images[self.STEAM_ICON_ID].ID,  # Use the custom Steam icon
                ).Create()
                Domoticz.Log(f"SteamPlugin: Created text device for game name '{steam_name} Game Name'")

            # Determine the selector level
            level = selector_levels.get(online_state.lower(), 0)
            
            # Create sValue with level name and game (for In-Game state)
            level_name = level_names.split("|")[level // 10]  # Get the level name
            sValue = f"{level_name}: {game_name}" if level == 20 else level_name
            
            # Update the selector switch
            Devices[1].Update(nValue=level, sValue=f"{level}")
            Domoticz.Log(f"SteamPlugin: Updated device with nValue={level}, sValue='{sValue}'")
            
            # If in-game, update the game name in the text device
            if level == 20:
                Devices[2].Update(nValue=0, sValue=game_name)  # Update text device with game name
                Domoticz.Log(f"SteamPlugin: Updated game name text device with value '{game_name}'")
            
            return True
        
        except requests.RequestException as e:
            Domoticz.Error(f"SteamPlugin: Error fetching Steam data: {str(e)}")
        except ET.ParseError as e:
            Domoticz.Error(f"SteamPlugin: Error parsing XML data: {str(e)}")
        return False


    def onStop(self):
        Domoticz.Log("SteamPlugin: Stopped")

    def onHeartbeat(self):
        if not self.initialized:
            Domoticz.Error("SteamPlugin: Plugin not properly initialized. Skipping heartbeat.")
            return
        Domoticz.Log("SteamPlugin: Heartbeat called")
        self.fetchSteamDetails()


global _plugin
_plugin = SteamPlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()
