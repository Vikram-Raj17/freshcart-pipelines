"""Publish sample food/ride requests to a RabbitMQ topic exchange."""

import argparse
import json
import os
import random
import time
import uuid
from datetime import datetime, timezone

import pika

EXCHANGE = "rapido-dispatch"
ZONES = {
    "bangalore": ["koramangala", "indiranagar", "whitefield"],
    "chennai": ["tnagar", "anna_nagar", "velachery"],
}
TYPES = ["ride", "food"]


def make_message(sequence: int, rng: random.Random, omit_zone: bool = False) -> tuple[str, dict]:
    city = rng.choice(list(ZONES))
    zone = rng.choice(ZONES[city])
    request_type = rng.choice(TYPES)
    routing_key = f"{city}.{zone}.{request_type}"
    message = {
        "id": str(uuid.uuid4()),
        "city": city,
        "type": request_type,
        "ts": datetime.now(timezone.utc).isoformat(),
    }
    # Every tenth message intentionally omits `zone` to test NACK handling.
    if not omit_zone:
        message["zone"] = zone
    return routing_key, message


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interval", type=float, default=2.0)
    parser.add_argument("--duration", type=float, default=120.0,
                        help="Seconds to publish; use 0 to run until Ctrl+C")
    parser.add_argument("--bad-every", type=int, default=10,
                        help="Omit zone on every Nth message; 0 disables bad messages")
    args = parser.parse_args()
    if args.interval <= 0 or args.duration < 0 or args.bad_every < 0:
        parser.error("interval must be > 0; duration and bad-every must be >= 0")

    url = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/%2F")
    params = pika.URLParameters(url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()
    channel.exchange_declare(exchange=EXCHANGE, exchange_type="topic", durable=True)

    rng = random.Random()
    sequence = 0
    deadline = time.monotonic() + args.duration if args.duration else None
    print(f"Publishing to topic exchange '{EXCHANGE}' every {args.interval}s")
    try:
        while deadline is None or time.monotonic() < deadline:
            sequence += 1
            # Use configured cadence (10th message is malformed by default).
            bad_every = args.bad_every
            city = rng.choice(list(ZONES))
            zone = rng.choice(ZONES[city])
            request_type = rng.choice(TYPES)
            key = f"{city}.{zone}.{request_type}"
            bad_message = bool(bad_every and sequence % bad_every == 0)
            message = {
                "id": str(uuid.uuid4()),
                "city": city,
                "type": request_type,
                "ts": datetime.now(timezone.utc).isoformat(),
            }
            if not bad_message:
                message["zone"] = zone
            body = json.dumps(message)
            channel.basic_publish(
                exchange=EXCHANGE,
                routing_key=key,
                body=body,
                properties=pika.BasicProperties(
                    content_type="application/json", delivery_mode=2
                ),
            )
            status = "BAD (zone omitted)" if "zone" not in message else "OK"
            print(f"PUBLISHED #{sequence} key={key} status={status} body={body}")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Dispatcher stopped by user")
    finally:
        if connection.is_open:
            connection.close()


if __name__ == "__main__":
    main()
