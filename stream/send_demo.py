"""Publish the D1 routing-key examples for deterministic routing checks."""
import json
import os
from datetime import datetime, timezone
import pika

EXCHANGE = "rapido-dispatch"
CASES = [
    ("bangalore.koramangala.food", {"id": "D1-1", "city": "bangalore", "zone": "koramangala", "type": "food"}),
    ("bangalore.indiranagar.ride", {"id": "D1-2", "city": "bangalore", "zone": "indiranagar", "type": "ride"}),
    ("bangalore.whitefield.ride", {"id": "D1-3", "city": "bangalore", "zone": "whitefield", "type": "ride"}),
    ("chennai.tnagar.food", {"id": "D1-4", "city": "chennai", "zone": "tnagar", "type": "food"}),
    ("chennai.whitefield.ride", {"id": "D1-5", "city": "chennai", "zone": "whitefield", "type": "ride"}),
    # Intentionally two words to test the bangalore.# pattern.
    ("bangalore.koramangala", {"id": "D1-6", "city": "bangalore", "zone": "koramangala", "type": "food"}),
]


def main():
    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")
    conn = pika.BlockingConnection(pika.URLParameters(url))
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)
    for key, message in CASES:
        message["ts"] = datetime.now(timezone.utc).isoformat()
        ch.basic_publish(exchange=EXCHANGE, routing_key=key, body=json.dumps(message),
                         properties=pika.BasicProperties(content_type="application/json", delivery_mode=2))
        print(f"PUBLISHED key={key} message={message}")
    conn.close()


if __name__ == "__main__":
    main()
