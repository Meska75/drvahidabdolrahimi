p = r"C:\Users\Asus\AppData\Local\Temp\neshan-leaflet.js"
s = open(p, encoding="utf-8", errors="ignore").read()
for key in ("dreamy", "maptype", "api-key", "Api-Key", ".png", "static.neshan"):
    i = 0
    n = 0
    print("====", key)
    while n < 4:
        i = s.find(key, i)
        if i < 0:
            break
        print(s[max(0, i - 100): i + 140].replace("\n", " "))
        print("---")
        i += len(key)
        n += 1
