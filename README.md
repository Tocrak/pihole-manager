## 🚦 Pi-hole Administration Proxy

This FastAPI application serves as a **proxy and simplified administration interface** for managing one or more **Pi-hole** instances. It centralizes client configuration, allowing users to easily toggle a device's Ad-Blocking status via a single web interface.

---

### ✨ Key Features

* **Multi-Pi-hole Support:** Manages clients and authentication across multiple Pi-hole endpoints.
* **Easy Client Toggling:** Provides a dashboard to move clients between pre-configured "Ad-Block Enabled" and "Ad-Block Disabled" groups with one click.
* **Automatic Auth/Session Refresh:** Handles Pi-hole API authentication (`sid`, `csrf`) in a background thread, ensuring sessions never expire.
* **Web Interface:** Simple, responsive dashboard with light/dark mode.

---

### ⚙️ Configuration (Environment Variables)

The application requires the following environment variables to connect and manage your Pi-holes:

| Variable | Description | Example |
| :--- | :--- | :--- |
| `ENDPOINTS` | Comma-separated list of full Pi-hole admin base URLs. | `http://pihole1/,http://pihole2/` |
| `PIHOLE_PASS` | The password for the Pi-hole Web Admin interface. | `MySecretPass` |
| `ADBLOCK_GROUP_ID` | The Pi-hole Group ID for **Ad-Blocking Enabled** clients. | `0` (Default) |
| `NON_ADBLOCK_GROUP_ID` | The Pi-hole Group ID for **Ad-Blocking Disabled** clients. | `1` (Default) |

---

### 🚀 Core Endpoints

| Method | Path | Function |
| :--- | :--- | :--- |
| `GET` | `/` | Web interface (Client Dashboard) |
| `GET` | `/clients` | Fetches client list from Pi-hole API |
| `POST` | `/editclient` | Updates client group/comment across **all** Pi-holes |
| `GET` | `/reboot` | Exits the application (for container restarts) |

---
