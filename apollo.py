import requests, time

class Weather:
    api = 'http://dataservice.accuweather.com/currentconditions/v1/'

    def __init__(self, key, loc='429728'):
        self.result = {}
        self.key = key
        self.loc = loc

    def __get(self):
        payload = {
            'apikey': self.key,
            'details': True
        }

        return requests.get(
            Weather.api + self.loc,
            params=payload,
            verify=False
        )

    def update(self):
        res = self.__get();
        status = res and res.status_code == 200

        if status:
            self.result = res.json()[0]

        return status

    def humidity(self):
        return self.result['RelativeHumidity']

    def temperature(self):
        return self.result['Temperature']['Metric']['Value']

class Line:
    api = 'https://api.line.me/v2/bot/'

    def __init__(self, token):
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }

    def broadcast(self, payload):
        res = requests.post(
            Line.api + 'message/broadcast',
            headers=self.headers,
            json=payload
        )

        return res and res.status_code == 200

    def create_texts(self, *texts):
        return {'messages': [
            *map(lambda t: {'type': 'text', 'text': t}, texts)
        ]}

def main():
    with open('tokens') as f:
        tokens = [*map(lambda s: s.rstrip('\n'), f.readlines())]

    line = Line(tokens[0])
    weather = Weather(tokens[1])

    while True:
        h = 0

        if weather.update():
            h = weather.humidity()

            messages = line.create_texts(
                (f'🌵【可開窗戶】' if h < 71 else f'💧【請關窗戶】') + \
                    f'\n目前外面的濕度為 {h}%'
            )

            if line.broadcast(messages):
                print(messages)
            else: print('cannot broadcast message')

        else: print('cannot update weather')

        time.sleep(3600)

__name__ == '__main__' and main()

