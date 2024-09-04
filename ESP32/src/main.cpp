// eduroam WPA2 Enterprise, TTLS, no certificate, MSCHAPv2(no EAP)
#include "esp_wpa2.h"
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <WiFi.h>
#define EAP_IDENTITY "bgrierson" // ID eg: "jonny" not jonny@univ.xx
#define EAP_PASSWORD "kvfnT5iwoe"

const char *ssid = "ITBA";
WiFiClient client;

void setup()
{
    Serial.begin(115200);
    delay(10);
    Serial.println();
    Serial.println(ssid);
    WiFi.disconnect(true);
    WiFi.mode(WIFI_STA);
    esp_wifi_sta_wpa2_ent_set_identity((uint8_t *)EAP_IDENTITY, strlen(EAP_IDENTITY));
    esp_wifi_sta_wpa2_ent_set_username((uint8_t *)EAP_IDENTITY, strlen(EAP_IDENTITY));
    esp_wifi_sta_wpa2_ent_set_password((uint8_t *)EAP_PASSWORD, strlen(EAP_PASSWORD));
    esp_wifi_sta_wpa2_ent_enable();

    Serial.println("MAC address: ");
    Serial.println(WiFi.macAddress());
    WiFi.begin(ssid);
    while (WiFi.status() != WL_CONNECTED)
    {
        delay(500);
        Serial.print(".");
    }
    Serial.println(WiFi.status());
    Serial.println(WL_CONNECTED);
    Serial.println("");
    Serial.println("IP address: ");
    Serial.println(WiFi.localIP());
    Serial.println(WiFi.status());
}

void loop()
{
    if (WiFi.status() == WL_CONNECTED)
    { // Check if the ESP32 is still connected to Wi-Fi
        HTTPClient http;

        // Specify the URL of the time API
        http.begin("http://worldtimeapi.org/api/timezone/Etc/UTC");

        // Send the HTTP GET request
        int httpResponseCode = http.GET();

        if (httpResponseCode > 0)
        {                                      // Check if the request was successful
            String payload = http.getString(); // Get the response payload as a string

            // Parse the JSON payload
            DynamicJsonDocument doc(1024);
            deserializeJson(doc, payload);

            // Extract the dateTime string from the JSON
            String dateTime = doc["datetime"];

            // Example datetime format: "2024-09-04T12:34:56.789Z"
            // Parse the dateTime into components
            String date = dateTime.substring(8, 10) + "/" + dateTime.substring(5, 7) + "/" + dateTime.substring(0, 4);
            String time = dateTime.substring(11, 19) + "." + dateTime.substring(20, 23);

            // Print the formatted date and time
            Serial.println("Formatted Date and Time: " + date + " - " + time);
        }
        else
        {
            Serial.println("Error on HTTP request: " + String(httpResponseCode));
        }

        // Free the resources
        http.end();
    }
    else
    {
        Serial.println("Wi-Fi not connected.");
    }

    delay(10000); // Wait for 10 seconds before making the next request
}