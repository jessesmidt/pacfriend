from typing import Dict, Any
import errors as PME
import os
import json


class JSONWork:
    def __init__(self, path: str):
        self.path: str = path
        self.comments_found: Dict[int, str] = dict([])
        self.inline_comments_found: Dict[int, str] = dict([])
        self.data: Any = None

    def load_json(self) -> None:
        """
        Loads the json of a file and saves the python style comments found
        """
        if not self.path or os.path.exists(self.path) is False:
            raise PME.NonExistingPath(self.path)
        if self.path.endswith(".json") is False:
            raise PME.InvalidJson(self.path)
        json_content: str = ""
        try:
            with open(self.path, "r") as file:
                for i, line in enumerate(file):
                    if line.strip().startswith("#"):
                        self.comments_found[i] = line
                        continue
                    elif '#' in line:
                        pos = line.index('#')
                        json_content += line[:pos].rstrip() + "\n"
                        self.inline_comments_found[i] = line[pos:]
                    else:
                        json_content += line
                self.data = json.loads(json_content)
        except json.JSONDecodeError:
            self.data = []

    def dump_json(self, data: Any) -> None:
        """
        Dumps the data into a json file and adds the
        previously existing comments

        Args
        data - The data which is goingto be dumped in a JSON file
        """
        if not self.path or os.path.exists(self.path) is False:
            raise PME.NonExistingPath(self.path)
        if self.path.endswith(".json") is False:
            raise PME.InvalidJson(self.path)
        if data is None:
            self.load_json()
        with open(self.path, "w") as file:
            json.dump(data, file, indent=2)
        full_content: str = ""
        off: int = 0
        count: int = 0
        with open(self.path, "r") as file:
            for i, line in enumerate(file):
                while i + off in self.comments_found.keys():
                    full_content += self.comments_found[i + off]
                    if full_content.endswith("\n") is False:
                        full_content += "\n"
                    off += 1
                full_content += line
                if i + off in self.inline_comments_found.keys():
                    full_content = full_content[:-1]
                    full_content += f" {self.inline_comments_found[i + off]}"
            if count != off:
                full_content += "\n"
            for key in self.comments_found.keys():
                if count < off:
                    count += 1
                    continue
                full_content += self.comments_found[key]
        with open(self.path, "w") as file:
            file.write(full_content)
