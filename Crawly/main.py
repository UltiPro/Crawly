import argparse
import re

from crawly import Crawly


url_regex = re.compile(
    r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"
)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "url",
        type=str,
        help="URL address of a website '-u <url>'.",
    )
    parser.add_argument(
        "--method",
        "-m",
        type=str,
        required=False,
        default="bfs",
        help=f"Method of search '-m <method>'. Only {Crawly.methods_string()} are allowed. Default: bfs.",
    )
    parser.add_argument(
        "--time",
        "-t",
        type=int,
        required=False,
        default=60,
        help="Maximum time of execution in seconds '-t <seconds>'. Default: 60.",
    )
    parser.add_argument(
        "--depth",
        "-d",
        type=int,
        required=False,
        default=10,
        help="Maximum depth of search '-d <value>'. Default: 10.",
    )
    args = parser.parse_args()

    # Validation

    if not url_regex.fullmatch(args.url):
        raise ValueError("Passed URL address is incorrect.")

    if args.method.upper() not in Crawly.methods():
        raise ValueError(f"Incorrect method. Only {Crawly.methods_string()} are allowed.")

    if args.time < 1:
        raise ValueError("Incorrect time. Time cannot be lower than 1 second.")

    if args.depth < 1:
        raise ValueError("Incorrect depth. Depth cannot be lower than 1.")

    # Crawly

    crawly = Crawly(args.url, args.method, args.time, args.depth)
    crawly.start()
