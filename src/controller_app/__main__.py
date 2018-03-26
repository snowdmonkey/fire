import argparse
import logging

from src.controller_app import create_app


def main():
    parser = argparse.ArgumentParser("run image analysis controller app")
    parser.add_argument("--db_uri", type=str, required=True, help="specify database uri")
    parser.add_argument("--mqtt_host", type=str, required=True, help="specify mqtt host")
    parser.add_argument("--mqtt_port", type=int, default=1883, help="specify mqtt port")
    parser.add_argument("--mqtt_user", type=str, required=True, help="specify mqtt user")
    parser.add_argument("--mqtt_pwd", type=str, required=True, help="specify mqtt password")

    args = parser.parse_args()

    app = create_app(db_uri=args.db_uri,
                     mqtt_host=args.mqtt_host,
                     mqtt_port=args.mqtt_port,
                     mqtt_user=args.mqtt_user,
                     mqtt_pwd=args.mqtt_pwd)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler()])

    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)


if __name__ == "__main__":
    main()