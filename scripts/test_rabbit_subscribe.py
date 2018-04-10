import pika


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


def main():
    connection = pika.BlockingConnection(pika.URLParameters("amqp://localhost:5672"))
    channel = connection.channel()
    channel.queue_declare(queue="alarm.equipment.move")

    channel.basic_consume(callback, queue="alarm.equipment.move", no_ack=True)
    channel.start_consuming()


if __name__ == "__main__":
    main()
