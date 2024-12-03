import os


def set_prices():
    price_RUB = {}
    price_USD = {}
    file_path = os.path.join("settings", "prices.txt")
    with open(file_path, encoding='utf-8') as file:
        currency = "RUB"
        for line in file.readlines():
            if "USD" in line:
                currency = "USD"

            try:
                if currency == "RUB":
                    price_RUB.update({line.split("=")[0]: line.split("=")[1].replace('\n', '')})
                else:
                    price_USD.update({line.split("=")[0]: line.split("=")[1].replace('\n', '')})
            except:
                pass
    return [price_RUB, price_USD]
