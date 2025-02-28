
#include "DHT.h"
#include <WiFi.h>
#include <PubSubClient.h>

#define WIFI_SSID "SSID"
#define WIFI_PASSWORD "PASSWD"

//MQTT Broker conf
const char* MQTT_HOST = "192.XXX.XXX.XXX";//IP ou hostname do servidor MQTT
const unsigned int MQTT_PORT = 7051;//Porta do servidor

WiFiClient espClient;
PubSubClient client(espClient);

// Tópicos do MQTT
#define MQTT_PUB_TEMP "esp32/dht/temperature"
#define MQTT_PUB_HUM  "esp32/dht/humidity"
#define MQTT_PUB_DB "esp32/dht/dbPopulate"

// GPIO no qual seu sensor está conectado
#define DHTPIN 4  

// Seleção do modelo de sensor a ser utilizado
//#define DHTTYPE DHT11   // DHT 11
#define DHTTYPE DHT22   // DHT 22  (AM2302), AM2321
//#define DHTTYPE DHT21   // DHT 21 (AM2301)   

// Inicialização DHT sensor
DHT dht(DHTPIN, DHTTYPE);

// Variaveis utilizadas para guardar leitura dos dados
float temp;
float hum;
char data[80];

unsigned long previousMillis = 0;   // Salva o tempo da ultima leitura
const long interval = 5000;        // Intervalo entre leituras EM MILISEGUNDOS, minimo sugerido 2 segundos.
void connectToWifi() {
  Serial.println("Connecting to Wi-Fi...");
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
}

void connectToMqtt() {
  // Loop de conexão mqtt
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");

    if (client.connect("ESPClient", "gstrgrad01", "GAinT3m9")) {
      Serial.println("connected");
      // Subscribe
      client.subscribe(MQTT_PUB_TEMP);
      client.subscribe(MQTT_PUB_HUM);
      client.subscribe(MQTT_PUB_DB);
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");

      delay(5000);
    }
  }
}

//Handler de eventos WiFi
void WiFiEvent(WiFiEvent_t event) {
  Serial.printf("[WiFi-event] event: %d\n", event);
  switch(event) {
    case ARDUINO_EVENT_WIFI_STA_GOT_IP:
      Serial.println("WiFi connected");
      Serial.println("IP address: ");
      Serial.println(WiFi.localIP());
      break;
    case ARDUINO_EVENT_WIFI_STA_DISCONNECTED:
      Serial.println("WiFi lost connection");
      break;
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println();

  dht.begin();
  
  client.setServer(MQTT_HOST, MQTT_PORT);
  WiFi.onEvent(WiFiEvent);
  connectToWifi();
}

void loop() {
  if (!client.connected()) {
    connectToMqtt();
  }
  client.loop();
  unsigned long currentMillis = millis();

  if (currentMillis - previousMillis >= interval) {
  
    previousMillis = currentMillis;
    //Nova Leitura
    hum = dht.readHumidity();
    // Temperatura em Celcius, para Farenheit adicione o parametro 'true'
    temp = dht.readTemperature();

    // Caso as leituras falhem, pode ser por má instalação, defeitos no sensor ou intervalo muito curto
    if (isnan(temp) || isnan(hum)) {
      Serial.println(F("Failed to read from DHT sensor!"));
      return;
    }

    // Tratamento e publicação da mensagem no respectivo tópico
    float hic = dht.computeHeatIndex(temp, hum, false);
    static char temperatureTemp[7];
    dtostrf(hic, 6, 2, temperatureTemp);

    static char humidityTemp[7];
    dtostrf(hum, 6, 2, humidityTemp);

    String dhtReadings = "{ \"temperature\": \"" + String(temperatureTemp) + "\", \"humidity\" : \"" + String(humidityTemp) + "\"}";
    dhtReadings.toCharArray(data, (dhtReadings.length() + 1));
    client.publish(MQTT_PUB_DB, data);                            
    Serial.printf("Publishing on topic %s: \n", MQTT_PUB_DB);
    Serial.println(data);
    // esp32/dht/temperature
    client.publish(MQTT_PUB_TEMP, String(temp).c_str());                            
    Serial.printf("Publishing on topic %s: \n", MQTT_PUB_TEMP);
    Serial.printf("Message: %.2f \n", temp);

    // esp32/dht/humidity
    client.publish(MQTT_PUB_HUM, String(hum).c_str());                            
    Serial.printf("Publishing on topic %s: \n", MQTT_PUB_HUM);
    Serial.printf("Message: %.2f \n", hum);
    
  }
}