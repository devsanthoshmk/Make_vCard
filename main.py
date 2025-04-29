import tablib
import textwrap
from tabulate import tabulate


class Contact:
    def __init__(self, filePath):
        self.filePath = filePath
        mode = (
            "rb" if self.filePath.lower().endswith((".xls", ".xlsx", ".ods")) else "r"
        )
        with open(self.filePath, mode) as f:
            content = f.read()
        self.table = tablib.Dataset().load(content)
        # except tablib.exceptions.UnsupportedFormat: handle this exception in object creation of this class
        self.fin_vcard = r""

    def show_table(self):
        print(tabulate(self.table.dict[:5], headers="keys", tablefmt="grid"))

    def escape_value(self, value: str) -> str:
        return (
            value.replace("\\", "\\\\")
            .replace(";", "\\;")
            .replace(",", "\\,")
            .replace("\n", "\\n")
        )

    def fold_line(self, line: str) -> str:
        """
        Fold lines longer than 75 characters according to vCard 3.0 spec.
        Continuation lines start with a single space.
        """
        if len(line) <= 75:
            return line
        parts = textwrap.wrap(line, width=75)
        return "\r\n".join([parts[0]] + [" " + part for part in parts[1:]])

    def add_contact(self, data: dict) -> str:
        """
        Generate a vCard 3.0 formatted string from provided data.
        """
        lines = [
            "BEGIN:VCARD",
            "VERSION:3.0",
            f"N:{self.escape_value(data['last_name'])};{self.escape_value(data['first_name'])};{self.escape_value(data.get('additional_names',''))};{self.escape_value(data.get('prefix',''))};{self.escape_value(data.get('suffix',''))}",
            f"FN:{self.escape_value(data['formatted_name'])}",
        ]

        if data.get("phone"):
            for ph in data["phone"]:
                lines.append(
                    x := f"TEL;TYPE={ph['typ']},VOICE:{self.escape_value(ph['phn'])}"
                )
            print(x)
        if data.get("email"):
            lines.append(f"EMAIL;TYPE=INTERNET,PREF:{self.escape_value(data['email'])}")
        if data.get("address"):
            adr = data["address"]
            lines.append(f"ADR;TYPE=HOME:;;{self.escape_value(adr)};;;;")
        if data.get("org"):
            lines.append(f"ORG:{self.escape_value(data['org'])}")
        if data.get("title"):
            lines.append(f"TITLE:{self.escape_value(data['title'])}")
        if data.get("url"):
            lines.append(f"URL:{self.escape_value(data['url'])}")

        lines.append("END:VCARD\n")

        # Fold long lines
        folded = [self.fold_line(line) for line in lines]
        return "\r\n".join(folded)

    def select_col(self):
        self.cols = {
            "first_name": self.table.headers[
                int(input("Enter the INDEX of column for first_name: ").strip())
            ],
            "last_name": (
                x := input(
                    "Enter the INDEX of column for last_name [optional]: "
                ).strip()
            )
            and self.table.headers[int(x)]
            or "",
            "formatted_name": (
                x := input(
                    "Enter the INDEX of column for formatted_name [optional]: "
                ).strip()
            )
            and self.table.headers[int(x)]
            or "",
            "additional_names": (
                x := input(
                    "Enter the INDEX of column for additional_names [optional]: "
                ).strip()
            )
            and self.table.headers[int(x)]
            or "",
            "prefix": (
                x := input("Enter the INDEX of column for prefix [optional]: ").strip()
            )
            and self.table.headers[int(x)]
            or "",
            "suffix": (
                x := input("Enter the INDEX of column for suffix [optional]: ").strip()
            )
            and self.table.headers[int(x)]
            or "",
            "phone": [
                list(
                    map(
                        lambda x: self.table.headers[int(x)],
                        input(
                            "Enter one or more INDICES of columns for phone (comma separated): "
                        ).split(","),
                    )
                ),
                [
                    i.upper()
                    if i.upper() in ["CELL", "WORK", "HOME", "VOICE"]
                    else "CELL"
                    for i in (
                        input(
                            "Enter the same number of type of phone number if empty defults to CELL(comma separated): "
                        ).split(",")
                        + ["0", "0", "0"]
                    )[:3]
                ],
            ],
            "email": (
                x := input("Enter the INDEX of column for email [optional]: ").strip()
            )
            and self.table.headers[int(x)]
            or "",
            "url": (
                x := input("Enter the INDEX of column for url [optional]: ").strip()
            )
            and self.table.headers[int(x)]
            or "",
            "bday": (
                x := input(
                    "Enter the INDEX of column for birthday [optional]: "
                ).strip()
            )
            and self.table.headers[int(x)]
            or "",
            "org": (
                x := input(
                    "Enter the INDEX of column for organization [optional]: "
                ).strip()
            )
            and self.table.headers[int(x)]
            or "",
            "title": (
                x := input("Enter the INDEX of column for title [optional]: ").strip()
            )
            and self.table.headers[int(x)]
            or "",
        }

        for row in self.table.dict:
            self.data = {
                "first_name": row[self.cols["first_name"]],
                "last_name": row[self.cols["last_name"]]
                if self.cols["last_name"]
                else "",
                "formatted_name": row[self.cols["formatted_name"]]
                if self.cols["formatted_name"]
                else row[self.cols["first_name"]] + self.cols["last_name"],
                "additional_names": row[self.cols["additional_names"]]
                if self.cols["additional_names"]
                else "",
                "prefix": row[self.cols["prefix"]] if self.cols["prefix"] else "",
                "suffix": row[self.cols["suffix"]] if self.cols["suffix"] else "",
                "phone": [
                    {"phn": row[phn], "typ": typ}
                    for phn, typ in zip(
                        self.cols["phone"][0],
                        self.cols["phone"][1],
                    )
                ],
                "email": row[self.cols["email"]] if self.cols["email"] else "",
                "url": row[self.cols["url"]] if self.cols["url"] else "",
                "bday": row[self.cols["bday"]] if self.cols["bday"] else "",
                "org": row[self.cols["org"]] if self.cols["org"] else "",
                "title": row[self.cols["title"]] if self.cols["title"] else "",
            }
            self.fin_vcard += self.add_contact(self.data)

    def create_vcard(self):
        with open("./contact.vcf", "w", encoding="utf-8") as f:
            f.write(self.fin_vcard)


obj = Contact("./test/table_data/table.csv")
obj.show_table()
obj.select_col()
obj.create_vcard()
