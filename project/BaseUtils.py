from typing import TextIO, List


class BaseParser:

    def __init__(self, parse_object: TextIO):
        self.parse_object = parse_object
        self.current_line = None

    def has_more_commands(self) -> bool:
        try:
            while True:
                current_line = next(self.parse_object)
                current_line = current_line.strip()
                if not current_line:
                    continue
                if (index := current_line.find("//")) >= 0:
                    if index == 0:
                        continue
                    else:
                        current_line = current_line.split("//")[0].strip()

                self.current_line = current_line
                break
        except StopIteration:
            return False
        except Exception as error:
            print(f"Get error {error}")
            raise error
        return True