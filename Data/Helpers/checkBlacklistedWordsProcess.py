import sys

from Data.Helpers import XMLBlacklist


def main():
    if len(sys.argv) < 2:
        exit(1)
    message = sys.argv[1].lower()
    blacklist = XMLBlacklist.load_blacklist()
    for word in blacklist:
        if word.lower() in message:
            exit(1)
    exit(0)

if __name__ == "__main__":
    main()