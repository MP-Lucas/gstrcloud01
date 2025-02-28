![USP Logo](https://www5.usp.br/storage/2024/01/usp-90anos-branco-w-550x179.png)

# Real Time Sensor Display - Display de leituras do sensor DHT22 em tempo real

## Descrição do Projeto

Este projeto visa disponibilizar um gráfico Valor x Tempo que exiba as leituras do sensor bem como armazenamento desses dados em um banco e filtro de data para consultas futuras.

![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Bootstrap](https://img.shields.io/badge/bootstrap-%238511FA.svg?style=for-the-badge&logo=bootstrap&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Socket.io](https://img.shields.io/badge/Socket.io-4.1.3-010101??style=flat-square&logo=Socket.io&logoColor=white)

#### Relatório Completo: https://www.overleaf.com/read/yhwbbkvvndkv#902ade
## Funcionalidades

- **Acompanhamento de dados em tempo real**
- **Filtro de data específica**

## Tecnologias Utilizadas

- **Frontend**: Bootstrap para estilização.
- **Backend**: Python Flask para comunicação com o banco de dados, HTML Canvas e JS para controle de eventos e gráficos.
- **Banco de dados**: PostgreSQL.
- **Comunicação**: Utilização de Python e Ajax SocketIO comunicação em tempo real via Websocket.

## Configuração e Execução

### Pré-requisitos

- Docker e Docker Compose instalados.
- Python 3.13 ou superior.
- Arduino IDE
- Microcontrolador ESP32 e Sensor de Temperatura e humidade DHT22 ou DHT11

### Instruções de Instalação

1. #### **Clone o Repositório ou faça download do zip**

   ```bash
   git clone https://github.com/ICMC-SSC0965-2024/gstrgrad01.git
   ```
2. #### **Configurando o codigo ESP**
   
   2.1. Certifique-se de que as seguintes bibliotecas estejam instaladas corretamende no ArduinoIDE:

     * [`DHT Sensor Library`](https://docs.arduino.cc/libraries/dht-sensor-library/) de Adafruit. 
     *  [`PubSubClient`](https://docs.arduino.cc/libraries/pubsubclient/) de Nick O'Leary

   2.2. No arquivo Arduino/sketch_nov21b/sketch_nov21b.ino, faça as seguintes alterações:

      * Substitua os defines `WIFI_SSID` e `WIFI_PASSWORD` pelo SSID da sua rede wifi e pela senha de acesso da rede, respectivamente.

      * O  `servidor MQTT` deverá apontar para `seu endereço IPv4` ou `hostname`, para isso basta alterar a contante `MQTT_HOST` para esse endereço. A porta deve ser mantida em 7051. No caso do ambiente virtual da usp o hostname é `andromeda.lasdpc.icmc.usp.br`

      * Se necessário altere a variável `DHTPIN` para o GPIO na qual está instalado o sensor ([Imagem de referência](#montagem-do-circuito)). Certifique-se também de verificar a variável `DHTTYPE` para que esteja de acordo com o sensor utilizado.

      * Faça upload do código para sua ESP.

   
3. #### **Construção e Execução com Docker Compose**
   
   Abra o terminal e navegue até a pasta raiz do projeto _/gstrgrad01_ use o comando:

   ```bash
   docker-compose up --build
   ```

   Este comando construirá as imagens Docker necessárias e iniciará os containers (talvez seja necessário sudo). O parâmetro `--build` garante que as imagens sejam reconstruídas, incorporando qualquer atualização nos Dockerfiles ou dependências.

### Acessando a Aplicação

#### Rodando a aplicação em localhost
Aplicação Web: http://localhost:5051/

#### Acessando a aplicação no domínio do ICMC
Aplicação Web: http://andromeda.lasdpc.icmc.usp.br:5051/ (Disponível apenas quando executado diretamente na vm)

5. #### **Instalação Manual (Alternativa sem Docker)**

   Se preferir rodar o projeto diretamente em seu ambiente local. 

      * Primeiramente crie uma base de dados PostgreSQL conforme o conteúdo do arquivo `gstrgrad01/setup/database/table.sql`.

      * Instale e inicie um servidor MQTT conforme este [tutorial linux](https://medium.com/@besnikbelegu/setting-up-an-mqtt-server-part-1-87b7bd7d30fd) ou este [tutorial windows](https://www.youtube.com/watch?v=2zzUIPHKtMk). Apenas as etapas de instalação e execução local são neccessárias.

      * Faça as alterações do [item 2](#configurando-o-codigo-esp).

      No arquivo app.py edite a seguinte linha: 
      ```bash
      mqttc.connect('<host>',<port>,60)
      ```

   >Onde Host deve ser o ip do seu servidor mqtt e porta configurada na instalação e execução do seu servidor mqtt conforme o item anterior e 60 é o tempo de keepalive sugerido.

   Logo em seguida, execute:
   ```bash
   pip install -r requirements.txt
   ```
   ```bash
   python app.py
   ```

### Acessando a Aplicação

#### Rodando a aplicação em localhost
Aplicação Web: http://localhost:5051/

## Overview da aplicação
#### Gráficos
![Visual](/static/img/fluxograma.png)
#### Filtro de data
![Seleção de data com dados](/static/img/selecao_normal.png)
#### Filtro com dados inexistentes
![Seleção de data sem dados](/static/img/selecao_vazia.png)

#### Montagem do Circuito
![Circuito](/static/img/circuito.jpeg)




## Aluno:

- Lucas Caetano Procópio
