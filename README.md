

# Domoticz Steam Plugin 🎮

**Plugin for Integrating Steam Status with Domoticz**

## 🌟 Overview

Easily monitor your Steam status within the Domoticz interface! This plugin fetches your Steam online/offline status and the current game you are playing, displaying it in Domoticz as selector switches and text devices.

## ⚡ Features

-   **Online/Offline Status:** Track whether you are online, offline, or in-game.
-   **Current Game:** Display the name of the game you are currently playing.
-   **Custom Icons:** Use Steam-themed icons for a sleek interface.
-   **Debugging Options:** Multiple levels of debugging for precise troubleshooting.

## 🛠 Installation

1.  **Download the Plugin:**
    -   Clone the plugin repository: `git clone https://github.com/galadril/Domoticz-Steam-Plugin`
    -   Navigate to the plugin directory: `cd Domoticz-Steam-Plugin`
2.  **Add to Domoticz:**
    -   Open the Domoticz interface and go to `Setup -> Hardware`.
    -   Select `Domoticz Steam Plugin` from the list of hardware types.
    -   Fill in the required fields such as SteamID and Debug level.
3.  **Install Dependencies:**
    -   Ensure you have the `requests` module installed: `pip install requests`

## ⚙️ Configuration

### Parameters

-   **SteamID:** Your unique SteamID. For instructions on finding your SteamID, visit: [SteamID Help](https://help.steampowered.com/en/faqs/view/2816-BE67-5B69-0FEC).
-   **Debug Level:** Choose the level of debug information you want to receive.

![SteamStatus](https://github.com/user-attachments/assets/794cb2ce-c8b9-4516-9737-db51f2d2a78f)![LatestGame](https://github.com/user-attachments/assets/32119072-ecf8-4dc5-b5d5-224bddab7b22)


## 🚀 Usage

### Status Levels

The selector switch uses the following levels:

-   **Offline:** Level 0
-   **Online:** Level 10
-   **In-Game:** Level 20

When you are in-game, the text device will automatically update with the name of the game you are playing.


## 📅 Change log
| Version | Information |
| ------- | ----------- |
|   0.0.1 | Initial version |
|   0.0.2 | Cache fixes on fetching Steam status |


## 🚀 Updates and Contributions
This project is open-source and contributions are welcome! Visit the GitHub repository for more information: [Domoticz-Steam-Plugin](https://github.com/galadril/Domoticz-Steam-Plugin).

## 🙏 Acknowledgements
- [Domoticz Plugin Wiki](https://www.domoticz.com/wiki/Plugins)

# ☕ Donation
If you like to say thanks, you could always buy me a cup of coffee (/beer)!
(Thanks!)
[![PayPal donate button](https://img.shields.io/badge/paypal-donate-yellow.svg)](https://www.paypal.me/markheinis)

