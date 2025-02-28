#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>

// Configurações do WiFi
const char* ssid = "NETID";
const char* password = "NETPASSWORD";

// Configurações do MQTT
//const char* mqtt_server = "andromeda.lasdpc.icmc.usp.br";
const char* mqtt_server = "andromeda.lasdpc.icmc.usp.br";
const char* mqtt_topic = "esp32/control";
const unsigned int mqtt_port = 6057;

// Autenticacao
const char * bot_id = "360";
const char * bot_password = "123";

WiFiClient espClient;
PubSubClient client(espClient);

// Definindo as portas GPIO que controlam os LEDs
const int ledPin1 = 13;
const int ledPin2 = 12;
const int ledPin3 = 25;
const int ledPin4 = 32;

// Configura o acesso ao wifi
void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Conectando-se a ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi conectado");
  Serial.println("Endereço IP: ");
  Serial.println(WiFi.localIP());
}

// Funcao que processa a mensagem recebida pelo MQTT
void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Mensagem recebida [");
  Serial.print(topic);
  Serial.print("] ");

  // Decodificando o json
  const size_t bufferSize = 1024;
  DynamicJsonDocument doc(bufferSize);
  DeserializationError error = deserializeJson(doc, payload);
  if (error) {
    Serial.print("deserializeJson() failed: ");
    Serial.println(error.c_str());
    return;
  }

  const char* ip = doc["ip"];
  const char* comando = doc["command"];
  const char* receivedID = doc["robot_id"];
  const char* receivedPassword = doc["robot_password"];

  Serial.print("\nIP RECEBIDO: ");
  Serial.println(ip);
  Serial.print("COMANDO RECEBIDO: ");
  Serial.println(comando);


  // Autenticacao basica
  if (!(!strncmp(bot_password, receivedPassword, strlen(bot_password)) && !strncmp(bot_id, receivedID, strlen(bot_id)))){
    return;
  }

 
  // Controle dos LEDs com base na mensagem recebida
  if (comando[0] == '1') {
    digitalWrite(ledPin1, HIGH);
  } else {
    digitalWrite(ledPin1, LOW);
  }

  if (comando[0] == '2') {
    digitalWrite(ledPin2, HIGH);
  } else {
    digitalWrite(ledPin2, LOW);
  }

  if (comando[0] == '3') {
    digitalWrite(ledPin3, HIGH);
  } else {
    digitalWrite(ledPin3, LOW);
  }

  if (comando[0] == '4') {
    digitalWrite(ledPin4, HIGH);
  } else {
    digitalWrite(ledPin4, LOW);
  }

  // Espera por um segundo
  delay(1000);

  // Apaga todos os LEDs
  digitalWrite(ledPin1, LOW);
  digitalWrite(ledPin2, LOW);
  digitalWrite(ledPin3, LOW);
  digitalWrite(ledPin4, LOW);

}

// Loop de conexao ao servidor MQTT
void reconnect() {
  while (!client.connected()) {
    Serial.print("Tentando conexão MQTT...");
    if (client.connect("ESP32Client")) {
      Serial.println("Conectado");
      client.subscribe(mqtt_topic);
    } else {
      Serial.print("falha, rc=");
      Serial.print(client.state());
      Serial.println(" tentando novamente em 5 segundos");
      delay(5000);
    }
  }
}

// Inicializacao
void setup() {
  Serial.begin(115200);
  Serial.print("test");
  delay(1000);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);

  // Configura as portas como saída
  pinMode(ledPin1, OUTPUT);
  pinMode(ledPin2, OUTPUT);
  pinMode(ledPin3, OUTPUT);
  pinMode(ledPin4, OUTPUT);
}

// Loop de verificacao de conexao
void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
