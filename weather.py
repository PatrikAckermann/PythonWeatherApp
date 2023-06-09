import requests
import json
import unitConversion

def searchCountry(countryName): # For searching a country code, understands local name and english name
    response = requests.get("https://restcountries.com/v3.1/name/" + countryName)
    if response.status_code == 200:
        response = json.loads(response.text)
        return [response[0]["cca2"], response[0]["translations"]["deu"]["common"]]
    else:
        return ["error", "error"]

def requestCoordinates(apiKey, city, state="none", country="none"):
    searchQuery = city
    if state != "none" and country != "none":
        searchQuery += "," + state
    if len(country) == 2:
        searchQuery += "," + country
    elif country != "none":
        searchQuery += "," + searchCountry(country)[0]
    
    output = []
    response = requests.get("http://api.openweathermap.org/geo/1.0/direct?q=" + searchQuery + "&limit=20&appid=" + apiKey)
    if response.status_code == 200:
        response = json.loads(response.text)
        for city in response:
            if "state" not in city:
                city["state"] = "Unbekannt"
            output.append([city["name"], city["lat"], city["lon"], city["state"], city["country"]])
        return output
    else:
        return "error"

def getCountryName(countryCode):
    response = requests.get("https://restcountries.com/v3.1/alpha/" + countryCode)
    if response.status_code == 200:
        response = json.loads(response.text)
        return response[0]["translations"]["deu"]["common"]

def requestCurrentWeatherData(apiKey, lat, lon):
    response = requests.get("https://api.openweathermap.org/data/2.5/weather?lat=" + lat + "&lon=" + lon + "&appid=" + apiKey)
    if response.status_code == 200:
        localTime = int(json.loads(response.text)["timezone"])
        return [json.loads(response.text), localTime]
    return [json.loads('{"coord":{"lon":0,"lat":0},"weather":[{"id":500,"main":"error","description":"error","icon":"10d"}],"base":"stations","main":{"temp":0,"feels_like":0,"temp_min":0,"temp_max":0,"pressure":0,"humidity":420},"visibility":0,"wind":{"speed":0,"deg":0},"rain":{"1h":0},"clouds":{"all":0},"dt":0,"sys":{"type":1,"id":0,"country":"Unknown","sunrise":0,"sunset":0},"timezone":0,"id":0,"name":"Unknown","cod":404}'), 0]

def requestWeatherData(apiKey, lat, lon): #46.94770812740157, 7.440220464189769
    response = requests.get("http://api.openweathermap.org/data/2.5/forecast?lat=" + lat +"&lon=" + lon + "&id=524901&appid=" + apiKey)
    if response.status_code == 200:
        return json.loads(response.text)
    return 404

def getWeather(self, main, description):
    img=""
    img2=""
    label=""
    bgColor = ""
    if main == "Clear" or description == "few clouds":
        img=self.window.sun
        img2=self.window.sunSmall
        label = self.translator.get("sunny")
        bgColor = "#41c2fa"
    elif description == "scattered clouds":
        img=self.window.cloudWithSun
        img2=self.window.cloudWithSunSmall
        label = self.translator.get("scatteredClouds").replace("oe", "ö")
        bgColor = "#41c2fa"
    elif main == "Clouds":
        img=self.window.cloud
        img2=self.window.cloudSmall
        label = self.translator.get("cloudy").replace("oe", "ö")
        bgColor = "#808080"
    elif main == "Rain" or main == "Drizzle":
        img=self.window.rain
        img2=self.window.rainSmall
        label = self.translator.get("rain")
        bgColor = "#808080"
    elif main == "Thunderstorm":
        img=self.window.thunder
        img2=self.window.thunderSmall
        label = self.translator.get("thunderstorm")
        bgColor = "#808080"
    elif main == "Mist" or main == "Haze" or main == "Fog":
        img=self.window.cloud
        img2=self.window.cloudSmall
        label = self.translator.get("foggy")
        bgColor = "#808080"
    elif main == "Smoke":
        img=self.window.cloud
        img2=self.window.cloudSmall
        label = self.translator.get("smoke")
        bgColor = "#808080"
    elif main == "Dust":
        img=self.window.cloud
        img2=self.window.cloudSmall
        label = self.translator.get("dust")
        bgColor = "#808080"
    elif main == "Sand":
        img=self.window.cloud
        img2=self.window.cloudSmall
        label = self.translator.get("sand")
        bgColor = "#c98a65"
    elif main == "Ash":
        img=self.window.cloud
        img2=self.window.cloudSmall
        label = self.translator.get("ash")
        bgColor = "#2b0300"
    elif main == "Squall":
        img=self.window.rain
        img2=self.window.rainSmall
        label = self.translator.get("storm")
        bgColor = "#808080"
    elif main == "Tornado":
        img=self.window.cloud
        img2=self.window.cloudSmall
        label = self.translator.get("tornado")
        bgColor = "#808080"
    else:
        img=self.window.error
        img2=self.window.errorSmall
        label=self.translator.get("error")
        bgColor = "red"
    
    return [img, img2, label, bgColor]

def formatWeatherData(weatherData, tempUnit, self):
    rtrn = []
    for list in weatherData["list"]:
        weather = getWeather(self, list["weather"][0]["main"], list["weather"][0]["description"])
        if tempUnit == "c":
            rtrn.append([weather[2], weather[0], weather[3], unitConversion.kelvinToCelsius(list["main"]["temp"]), list["dt"], weather[1], list["main"]["temp_min"], list["main"]["temp_max"], ])
        else:
            rtrn.append([weather[2], weather[0], weather[3], unitConversion.kelvinToFahrenheit(list["main"]["temp"]), list["dt"], weather[1], list["main"]["temp_min"], list["main"]["temp_max"], ])
    return rtrn