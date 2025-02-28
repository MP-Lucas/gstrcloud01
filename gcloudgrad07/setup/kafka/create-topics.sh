#!/bin/bash
# Kafka topic creation script using Kafka brokers

# Constants
TOPIC_NAME01="user-events"
TOPIC_NAME02="robot-events"
TOPIC_NAME03="robot-control"
PARTITIONS=1
REPLICATION_FACTOR=1
BROKER_LIST=broker:9092  # Make sure the broker list matches your Kafka service

# Wait for Kafka to be ready
#echo "Waiting for Kafka to start listening on $BROKER_LIST"
#@while ! nc -z $(echo $BROKER_LIST | cut -d: -f1) $(echo $BROKER_LIST | cut -d: -f2); do sleep 5; done

# Create Kafka topic
kafka-topics --create --if-not-exists --bootstrap-server $BROKER_LIST --replication-factor $REPLICATION_FACTOR --partitions $PARTITIONS --topic $TOPIC_NAME01
kafka-topics --create --if-not-exists --bootstrap-server $BROKER_LIST --replication-factor $REPLICATION_FACTOR --partitions $PARTITIONS --topic $TOPIC_NAME02
kafka-topics --create --if-not-exists --bootstrap-server $BROKER_LIST --replication-factor $REPLICATION_FACTOR --partitions $PARTITIONS --topic $TOPIC_NAME03

INIT_MSG="init"

# Tópico 1
echo "$INIT_MSG" | kafka-console-producer --bootstrap-server $BROKER_LIST --topic $TOPIC_NAME01

# Tópico 2
echo "$INIT_MSG" | kafka-console-producer --bootstrap-server $BROKER_LIST --topic $TOPIC_NAME02

# Tópico 3
echo "$INIT_MSG" | kafka-console-producer --bootstrap-server $BROKER_LIST --topic $TOPIC_NAME03