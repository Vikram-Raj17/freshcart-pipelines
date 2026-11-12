"""Consume messages matching a driver's RabbitMQ topic binding."""

import argparse
import json
import os
import uuid

import pika

EXCHANGE = "rapido-dispatch"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Driver display name")
    parser.add_argument("pattern", help="RabbitMQ topic binding pattern")
    args = parser.parse_args()

    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")
    connection = pika.BlockingConnection(pika.URLParameters(url))
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    declared = channel.queue_declare(queue="", exclusive=True, auto_delete=True)
    queue_name = declared.method.queue
    channel.queue_bind(exchange=EXCHANGE, queue=queue_name, routing_key=args.pattern)
    channel.basic_qos(prefetch_count=1)

    print(f"{args.name}: queue={queue_name}; binding={args.pattern}")

    def handle_message(ch, method, properties, body):
        try:
            message = json.loads(body.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            print(f"{args.name}: NACK invalid JSON; routing_key={method.routing_key}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        if not isinstance(message, dict) or not message.get("zone"):
            print(f"{args.name}: NACK missing zone; routing_key={method.routing_key}; body={message}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            return

        print(f"{args.name}: RECEIVED routing_key={method.routing_key} message={message}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=handle_message, auto_ack=False)
    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print(f"{args.name}: stopping")
    finally:
        if channel.is_open:
            channel.stop_consuming()
        if connection.is_open:
            connection.close()


if __name__ == "__main__":
    main()
