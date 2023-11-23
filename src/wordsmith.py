from src.generation import Etymologist, Neologist
from src.customio import Reader, Writer
from functools import partial


class WordSmith:

    INV_CMD_MSG = "Invalid command. Enter 'help' for a list of commands.\n"
    ERR_MSG = "An error occured. Check the arguments you provided to your previous command.\n"

    @staticmethod
    def _compress(iterable):
        index = 0
        while index + 1 < len(iterable):
            yield iterable[index], iterable[index + 1]
            index += 2

    def __init__(self):
        self._is_active = False

        self._reader = Reader
        self._writer = Writer
        # I/O classes are intentionally not instantiated, as they are merely
        # collections of class methods and class attributes.

        self._index = Etymologist()
        self._builder = Neologist()

        self._definitions = {}
        self._sources = {}

        self._commands = {
            "add"    : ("<file> as <type name> ", self.add_type),
            "new"    : ("[<number> <type>]xN", self.generate_word),
            "old"    : ("", self._list_words),
            "exit"   : ("", self.stop),
            "help"   : ("", self._list_commands),
            "alias"  : ("<name> as <command> <args> ", self._alias_command),
            "types"  : ("", self._list_sources),
            "export" : ("<file> ", self._export_words),
            "remove" : ("<type name> ", self.remove_type),
        }
    
    def _alias_command(self, *args):
        """
        Allows a single string to stand-in for a full command.
        """
        alias = args[0]
        given = args[2:]
        if alias in self._commands or given[0] not in self._commands:
            msg = f"Invalid alias passed to {repr(type(self).__name__)}"
            raise ValueError(msg)
        func = partial(self.execute, *given)
        desc = f"Aliased to {repr(' '.join(str(x) for x in given))}"
        func.__doc__ = desc
        self._commands[alias] = ("", func)

    def _display_as_paragraph(self, word, definition):
        self._writer.to_user(
            self._writer.as_lexicograph(word, definition) + "\n",
            "random"
        )

    def _export_words(self, *args):
        """
        Saves the words which have already been generated to a text file.
        """
        path = args[0]
        self._writer.to_file(path, "", overwrite=True)
        for word, definition in self._definitions.items():
            self._writer.to_file(path, self._as_line(word, definition), overwrite=False)

    def _list_commands(self, *args):
        """
        Lists every WordSmith valid command.
        """
        for cmd, (desc, func) in self._commands.items():
            self._writer.to_user(f"{cmd + ' ' + desc:35}- {func.__doc__.strip()}\n")

    def _list_sources(self):
        """
        Lists the text file each term type is mapped to.
        """
        for k, v in self._sources.items():
            self._writer.to_user(f"{k} -> {v}\n")

    def _list_words(self):
        """
        Lists the words which have already been generated.
        """
        if len(self._definitions):
            for word, definition in self._definitions.items():
                self._writer.to_user(self._as_line(word, definition))
        else:
            self._writer.to_user("No words generated\n", "blue")

    def _as_key(self, string):
        return string.strip().lower()

    def _as_line(self, word, definition):
        return f"{word.capitalize():20} | {definition.capitalize()}.\n"

    def add_type(self, *args):
        """
        Adds a new term type.
        """
        path, term_type = args[0], self._as_key(args[2])
        self.remove_type(term_type)
        self._sources[term_type] = path
        terms = {k: v for k, v in self._reader.from_file(path, "=")}
        self._index.add_terms(term_type, terms)

    def remove_type(self, *args):
        """
        Removes an existing term type.
        """
        term_type = self._as_key(args[0])
        if term_type in self._sources:
            self._sources.pop(term_type)
            self._index.remove_terms(term_type)

    def generate_word(self, *args):
        """
        Generates a new word.
        """
        for count, term_type in self._compress(args):
            used = set()
            for _ in range(count):
                term = None
                while term is None or term in used:
                    term, meaning = self._index.get_term_of_type(term_type)
                used.add(term)
                self._builder.push(term, meaning)
        word, definition = self._builder.pull()
        self._definitions[word] = definition
        self._display_as_paragraph(word, definition)

    def stop(self, *args):
        """
        Exits WordSmith.
        """
        self._is_active = False

    def start(self):
        self._is_active = True
        while self._is_active:
            response = self._reader.from_user()
            self.execute(*response)

    def execute(self, cmd, *args):
        if cmd in self._commands:
            func = self._commands[cmd][1]
            try:
                func(*args)
            except Exception as e:
                self._writer.to_user(str(e) + "\n", "red")
        else:
            self._writer.to_user(self.INV_CMD_MSG, "red")

