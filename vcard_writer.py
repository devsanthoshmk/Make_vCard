import textwrap


def escape_value(value: str) -> str:
    """
    Escape special characters in vCard values.
    """
    return (
        value.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace("\n", "\\n")
    )


def fold_line(line: str) -> str:
    """
    Fold lines longer than 75 characters according to vCard 3.0 spec.
    Continuation lines start with a single space.
    """
    if len(line) <= 75:
        return line
    parts = textwrap.wrap(line, width=75)
    return "\r\n".join([parts[0]] + [" " + part for part in parts[1:]])


def create_vcard(data: dict) -> str:
    """
    Generate a vCard 3.0 formatted string from provided data.
    """
    lines = [
        "BEGIN:VCARD",
        "VERSION:3.0",
        f"N:{escape_value(data['last_name'])};{escape_value(data['first_name'])};{escape_value(data.get('additional_names',''))};{escape_value(data.get('prefix',''))};{escape_value(data.get('suffix',''))}",
        f"FN:{escape_value(data['formatted_name'])}",
    ]

    if data.get("phone"):
        for ph in data["phone"]:
            lines.append(f"TEL;TYPE={ph['typ']},VOICE:{escape_value(ph['phn'])}")
    if data.get("email"):
        lines.append(f"EMAIL;TYPE=INTERNET,PREF:{escape_value(data['email'])}")
    if data.get("address"):
        adr = data["address"]
        lines.append(f"ADR;TYPE=HOME:;;{escape_value(adr)};;;;")
    if data.get("org"):
        lines.append(f"ORG:{escape_value(data['org'])}")
    if data.get("title"):
        lines.append(f"TITLE:{escape_value(data['title'])}")
    if data.get("url"):
        lines.append(f"URL:{escape_value(data['url'])}")
    if data.get("bday"):
        lines.append(f"BDAY:{escape_value(data['bday'])}")

    lines.append("END:VCARD\n")

    # Fold long lines
    folded = [fold_line(line) for line in lines]
    return "\r\n".join(folded)


if __name__ == "__main__":
    print("Let's collect details for your vCard (v3.0)")
    data = {}
    data["first_name"] = input("First name: ").strip()
    data["last_name"] = input("Last name: ").strip()
    data["additional_names"] = input(
        "Additional names (middle, etc.) [optional]: "
    ).strip()
    data["prefix"] = input("Name prefix (Mr., Dr.) [optional]: ").strip()
    data["suffix"] = input("Name suffix (Jr., III) [optional]: ").strip()
    # Formatted name default to "First Last"
    data["formatted_name"] = (
        input(
            f"Formatted name [default '{data['first_name']} {data['last_name']}']: "
        ).strip()
        or f"{data['first_name']} {data['last_name']}"
    )

    data["phone"] = []
    phn = {"phn": input("Phone number [optional]: ").strip()}
    if phn:
        phn["typ"] = (
            input("Phone type (CELL, HOME, WORK) [default CELL]: ").strip().upper()
            or "CELL"
        )
        data["phone"].append(phn)
    while True:
        if (
            input("Do you want to add an another phone number? (y/N): ").strip().lower()
            == "y"
        ):
            data["phone"].append(
                {
                    "phn": input("Phone Number :"),
                    "typ": input("Phone type (CELL, HOME, WORK) [default CELL]: ")
                    .strip()
                    .upper()
                    or "CELL",
                }
            )
        else:
            break

    data["email"] = input("Email address [optional]: ").strip()

    # Address block
    use_addr = input("Do you want to add an address? (y/N): ").strip().lower() == "y"
    if use_addr:
        adr = input("Enter Your address: ")

    # aditinal
    data["org"] = input("Organization [optional]: ").strip()
    data["title"] = input("Job title [optional]: ").strip()
    data["url"] = input("Website URL [optional]: ").strip()
    data["bday"] = input("BDAY  (YYYY-MM-DD) [optional]: ").strip()

    print(data)
    vcard_str = create_vcard(data)
    filename = (
        input("Enter filename for vCard [default contact.vcf]: ").strip()
        or "contact.vcf"
    )
    with open(filename, "w", encoding="utf-8") as f:
        f.write(vcard_str + "\r\n")

    print(f"vCard saved to {filename}")
