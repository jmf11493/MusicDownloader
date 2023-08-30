import re


class Validator:

    @staticmethod
    def string_clean(input_string: str):
        replacements = ["\\", "/", "|", "*", ":", "?", ">", "<", "\"", "[", "]", ",", "{", "}"]

        for remove_char in replacements:
            input_string = input_string.replace(remove_char, "")
        input_string.replace("&amp;", "&")

        # Remove all non ascii characters
        return re.sub(r'[^\x00-\x7f]', '', input_string)

