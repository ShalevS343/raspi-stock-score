from model import Model

def main():
    default_stocks = [
        "SIRI", "F", "PBR", "UAA", "UBER", "NIO", "SPCE",
        "NOK", "INO", "GRPN", "NCLH", "KODK",
        "HTZ", "CZR", "CCL", "NKLA", "TSLA", "RKT", "GME", "FUBO", "PLUG", "RIOT",
        "SNAP", "ROKU", "CLOV", "BB", "SPWR", "CLNE"
    ]

    
    diffs = []
    for stock in default_stocks:
        model = Model(stock)
        diff = model.start()
        diffs.append([stock, diff[0] if not isinstance(diff, int) else diff])
    
    print(diffs)
        
if __name__ == "__main__":
    main()