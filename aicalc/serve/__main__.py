"""python3 -m aicalc.serve [--port 8573] [--open]"""
import argparse
import webbrowser

from .http import serve


def main() -> None:
    parser = argparse.ArgumentParser(prog="python3 -m aicalc.serve",
                                     description="Kaizo AI battle simulator")
    parser.add_argument("--port", type=int, default=8573)
    parser.add_argument("--open", action="store_true",
                        help="open the UI in the default browser")
    args = parser.parse_args()

    server = serve(args.port)
    url = f"http://127.0.0.1:{args.port}/"
    print(f"aicalc simulator at {url}  (Ctrl-C to stop)")
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
