import pika


def main():
    connection = pika.BlockingConnection(pika.URLParameters("amqp://localhost:5672"))
    channel = connection.channel()
    channel.queue_declare(queue="alarm.equipment.move")

    for i in range(10):
        channel.basic_publish(exchange="alarm.equipment.move",
                              routing_key="alarm.equipment.move.#",
                              body="MESSAGE {}".format(i))
    connection.close()

if __name__ == "__main__":
    main()