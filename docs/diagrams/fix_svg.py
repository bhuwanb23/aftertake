from pathlib import Path

for p in Path(".").glob("*.svg"):
    data = p.read_bytes()
    out = bytearray()
    for b in data:
        if b < 32 and b not in (9, 10, 13):
            if b == 0x19:
                out.extend(b"--")
            elif b == 0x18:
                out.extend(b"-")
            elif b in (0x1C, 0x1D):
                out.append(ord("'"))
            elif b == 0x14:
                out.append(ord("*"))
            else:
                out.append(ord("?"))
        else:
            out.append(b)
    p.write_bytes(bytes(out))
    print(f"fixed {p.name}")
