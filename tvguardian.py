import re

def trimmedpage(eep : bytes, pgnum : int) -> bytes:
    page = eep[pgnum * 256:(pgnum+1) * 256]
    endmarker = page.find(b'\xff')
    if endmarker == -1:
        raise ValueError("Unterminated EEPROM page")
    return page[0:endmarker]

PAGENAMES = ["A-C", "D-F", "G-I", "J-O", "P-S", "T-Z"]

if __name__ == "__main__":
    with open("EEPROM_dump.bin", "rb") as eeprom_file:
        eeprom_data = eeprom_file.read()
    substitutes = [w.decode('ASCII') for w in trimmedpage(eeprom_data,6).split(b'\x00')[1:-1]]
    print("Substitute list")
    for i, word in enumerate(substitutes):
        print (i, word)
    for (num, name) in enumerate(PAGENAMES):
        print("Page", name)
        data = trimmedpage(eeprom_data, num)
        for (word_,flags,action_) in re.findall(b"([ -Z]*)([\0\1\2]*)([\x80-\xdf])", data):
            word = word_.decode("ASCII")
            action = action_[0]
            prefix = "whole word" if b'\x00' in flags else "starts with"
            f1 = "FLAG1" if b'\x01' in flags else ""
            f2 = "FLAG2" if b'\x02' in flags else ""
            action_name = f"action {action:x}"
            if action >= 0x80 and action <= 0x9F:
                action_name = f"replace with '{substitutes[action-0x80]}'"
            if action == 0xA0:
                action_name = "allow"
            if action == 0xA1:
                action_name = "merge"
            if action >= 0xC0 and action <= 0xDF:
                action_name = f"replace with '{substitutes[action-0xC0]}' if strict"
            print(f"{prefix:11} {word:20} {action_name:40} {f1}{f2}")
