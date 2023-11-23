from src.wordsmith import WordSmith
from src.customio import Reader, Writer


def main():
    app = WordSmith()

    commands = Reader.from_file("wordsmithrc")
    for command in commands:
        app.execute(*command)

    app.start()


if __name__ == "__main__":
    main()

