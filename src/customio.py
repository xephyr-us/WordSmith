from random import choice


COLOR_RESET_CHAR = "\033[0m"


class Reader:

    PROMPT = f"{COLOR_RESET_CHAR}?> "

    @staticmethod
    def _process_string(string, delimiter):
        return tuple(int(x) if x.isnumeric() else x.lower().strip() for x in string.strip().split(delimiter))

    @classmethod
    def from_user(cls, delimiter=" "):
        response = input(cls.PROMPT)
        return cls._process_string(response, delimiter)
    
    @classmethod
    def from_file(cls, path, delimiter=" "):
        output = []
        try:
            with open(path, "r") as opened:
                output = [
                    cls._process_string(s, delimiter)
                    for s in opened.readlines() 
                    if cls._process_string(s, delimiter)
                ]
        except FileNotFoundError:
            pass
        return output


class Writer:

    COLORS = {
        "red":     "\033[1;31m",
        "green":   "\033[1;32m",
        "yellow":  "\033[1;33m",
        "blue":    "\033[1;34m",
        "magenta": "\033[1;35m",
        "cyan":    "\033[1;36m",
        "white":   "\033[1;37m",
    }

    COLOR_NAMES = tuple(COLORS.keys())

    PADDING = "~"
    DIVIDER = "="

    @staticmethod
    def _as_paragraph(text, width):
        output = ""
        line_length = 0
        for word in text.capitalize().split():
            word_length = len(word) + 1
            line_length += word_length
            if line_length > width:
                output += "\n"
                line_length = word_length
            output += word + " "
        output = output[:-1] + "."
        return output
            
    @staticmethod
    def to_file(path, message, overwrite=False):
        mode = "w" if overwrite else "a"
        with open(path, mode) as opened:
            opened.write(message)

    @classmethod
    def _get_color_char(cls, name=""):
        try:
            key = name.strip().lower()
        except AttributeError:
            msg = f"Argument 'color' of non-string type passed to {repr(type(cls).__name__)}"
            raise TypeError(msg)
        if key == "random":
            key = choice(cls.COLOR_NAMES)
        if key:
            return cls.COLORS[key]
        return COLOR_RESET_CHAR

    @classmethod 
    def to_user(cls, message, color=""):
        color_char = cls._get_color_char(color)
        print(f"{color_char}{message}", end=COLOR_RESET_CHAR)

    @classmethod
    def as_lexicograph(cls, word, definition, width=20):
        padding_size = width - (len(word) + 2) // 2
        padding = cls.PADDING * padding_size
        header = f"{padding} {word.title()} {padding}"
        true_width = len(header)
        divider = cls.DIVIDER * true_width
        paragraph = cls._as_paragraph(definition, true_width)
        return f"{divider}\n{header}\n{divider}\n{paragraph}\n"

