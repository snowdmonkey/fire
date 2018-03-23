from controller_app import create_app
import argparse
import logging


def main():
    parser = argparse.ArgumentParser("run image analysis controller app")
    parser.add_argument("--db_uri", type=str, required=True, help="specify database uri")

    args = parser.parse_args()

    app = create_app(db_uri=args.db_uri)

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler()])

    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)


if __name__ == "__main__":
    main()