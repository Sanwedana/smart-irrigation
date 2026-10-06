# 🌱 Smart Irrigation System

An IoT-based Smart Irrigation System that monitors soil moisture and helps automate water pump control using an ESP8266, relay module, and ThingSpeak.

## 📌 Features

- 🌱 Soil moisture monitoring
- 💧 Automatic water pump control
- 📡 ESP8266-based IoT communication
- 🔌 Relay module for controlling the pump
- ☁️ ThingSpeak for storing and retrieving sensor data
- 📊 Streamlit dashboard for monitoring data
- 🔐 API keys stored securely using environment variables

## 🏗️ System Architecture

```text
Soil Moisture Sensor
        ↓
     ESP8266
        ↓
   ThingSpeak
        ↓
 Streamlit Dashboard
        ↓
 Pump Control
        ↓
    Relay Module
        ↓
    Water Pump
```

## 📁 Project Structure

```text
smart-irrigation/
│
├── app.py
├── requirements.txt
├── .env
├── .env.example
├── .gitignore
└── README.md
```

## ⚙️ Technologies Used

- Python
- Streamlit
- ESP8266 / NodeMCU
- ThingSpeak
- Soil Moisture Sensor
- Relay Module
- Water Pump
- Pandas
- REST API

## 🔐 Environment Variables

Create a `.env` file in the project root:

```env
THINGSPEAK_READ_API_KEY=your_read_api_key
THINGSPEAK_WRITE_API_KEY=your_write_api_key
```

Never upload the `.env` file to GitHub.

The `.gitignore` file is configured to prevent the `.env` file from being committed.

## 🚀 Installation

Clone the repository:

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd smart-irrigation
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Create the `.env` file and add your ThingSpeak API keys.

## ▶️ Run the Dashboard

Run:

```bash
streamlit run app.py
```

The Streamlit dashboard will open in your browser.

## 🔑 ThingSpeak Configuration

The application uses ThingSpeak API keys to securely access channel data.

The Read API Key is used to retrieve sensor data.

The Write API Key can be used when the system needs to send or update data through ThingSpeak.

## 🔌 Hardware Components

- NodeMCU ESP8266
- Soil Moisture Sensor
- Relay Module
- DC Water Pump
- External Power Supply
- Connecting Wires

## 🌊 Working

1. The soil moisture sensor measures the moisture level of the soil.
2. The ESP8266 reads the sensor value.
3. Sensor data is sent to ThingSpeak.
4. The Streamlit dashboard retrieves and displays the data.
5. Based on the irrigation condition, the pump can be controlled.
6. The relay acts as an electrically controlled switch between the ESP8266 and water pump.

## ⚠️ Security

API keys and other credentials should never be hard-coded in `app.py` or uploaded to GitHub.

Use the `.env` file for private credentials and `.env.example` as a template for other users.

## 👩‍💻 Project

Smart Irrigation System — IoT + Cloud + Streamlit Dashboard
