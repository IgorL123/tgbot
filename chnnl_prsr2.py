import requests
from bs4 import BeautifulSoup

class TgChannels:
    def __init__(self):
        self.url = ''
        self.html = self.get_html()

    def get_html(self):
        try:
            result = requests.get(self.url)
            result.raise_for_status()
            return result.text
        except(requests.RequestException, ValueError):
            print("Server error")
            return False

    def get_channels_tg(self):
        soup = BeautifulSoup(self.html,"html.parser")
        channels_list = soup.findAll('a', class_="channel-item")
        return channels_list

if __name__ == "__main__":
    channels = TgChannels()
    channels = channels.get_channels_tg()
    for i in range(len(channels)):
        x = str(channels[i])
        i1 = x.find('"/channel/')
        i2 = x.find('?start=')
        x = x[i1 + 10: i2]
        channels[i] = x
    tgdata = open('/Users/Zeden/Desktop/Tgdatafinal.txt','a')
    for i in channels:
        tgdata.write(i + "\n")
    tgdata.close()