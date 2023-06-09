# Pypi modules
import time
import tkinter as tk
from tkinter import ttk
from threading import Thread
import json
import datetime
from os.path import exists
from tkinter import messagebox
import geocoder

# Self made modules
from langtranslator import langtranslator #langtanslator.py
import weather #weather.py
import unitConversion as uc #unitConversion.py

close = False

class programWindow:
    def __init__(self, apiKey):
        self.apiKey = apiKey
        self.currentCoords = geocoder.ip("me").latlng
        self.currentCoords[0] = str(self.currentCoords[0])
        self.currentCoords[1] = str(self.currentCoords[1])

        if not exists("json/settings.json"):
            file = open("json/settings.json", "w")
            file.write(json.dumps({'language': 'en', 'temperatureUnit': 'c', 'timezone': 'own'}))
            file.close()
        self.settings = self.loadSettings()

        self.translator = langtranslator("json/translations.json", self.settings["language"])

        self.window = tk.Tk()

        self.sideBarWidth = 50

        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)

        self.currentFrame = -1

        self.window.update()
        self.sideBarCanvas = tk.Canvas(bg="black", width=self.sideBarWidth, highlightthickness=0)
        self.weatherFrame = tk.Frame(bg="#41c2fa")
        self.citiesFrame = tk.Frame(bg="#41c2fa")
        self.settingsFrame = tk.Frame(bg="#41c2fa")

        self.sideBarSymbols = []

        self.chooseCircle = self.sideBarCanvas.create_oval(5, 5, 60, 60, fill="#41c2fa", tag="chooseCircle")
        self.chooseCirclePositions = [[5, 5, 60, 60], [5, 45, 60, 100], [5, 520, 60, 575]]
        self.symbolPositions = [[[8, 5], [12, 13], [5, 5]], [[7, 50], [12, 53], [7, 65]], [[7, 515], [12, 529], [7, 535]]]

        self.sideBarCanvas.grid(row=0, column=0, sticky="NWS")
        self.weatherFrame.grid(row=0, column=1, sticky="NSWE", padx=3, pady=3)

        # WEATHER FRAME CONTENT
        self.localTime = 0

        self.window.logo = tk.PhotoImage(file="img/logo.png")
        self.window.sun = tk.PhotoImage(file="img/sun.png").subsample(2)
        self.window.rain = tk.PhotoImage(file="img/rain.png").subsample(2)
        self.window.cloud = tk.PhotoImage(file="img/cloud.png").subsample(2)
        self.window.cloudWithSun = tk.PhotoImage(file="img/weatherSymbol.png").subsample(2)
        self.window.thunder = tk.PhotoImage(file="img/thunderstorm.png").subsample(2)
        self.window.error = tk.PhotoImage(file="img/error.png").subsample(2)
        self.window.sunSmall = tk.PhotoImage(file="img/sun.png").subsample(16)
        self.window.rainSmall = tk.PhotoImage(file="img/rain.png").subsample(16)
        self.window.cloudSmall = tk.PhotoImage(file="img/cloud.png").subsample(16)
        self.window.cloudWithSunSmall = tk.PhotoImage(file="img/weatherSymbol.png").subsample(16)
        self.window.thunderSmall = tk.PhotoImage(file="img/thunderstorm.png").subsample(16)
        self.window.errorSmall = tk.PhotoImage(file="img/error.png").subsample(16)

        self.window.call("wm", "iconphoto", self.window._w, self.window.logo)
        self.window.title(self.translator.get("title"))

        self.placeName = tk.Label(self.weatherFrame, text="Unknown", font=("Arial", 20), fg="#ffffff")
        self.placeName.grid(row=0, column=0, columnspan=2)

        self.currentWeatherImg = tk.Canvas(self.weatherFrame, bg="#41c2fa", highlightthickness=0, width=250, height=250)
        self.currentWeatherImg.grid(row=1, column=0, rowspan=2)
        self.weatherImg = self.currentWeatherImg.create_image(0, 0, anchor="nw", image=self.window.error)

        self.currentWeatherLabel = tk.Label(self.weatherFrame, text="Error", font=("Arial", 30), bg="#41c2fa", fg="#ffffff")
        self.currentWeatherLabel.grid(row=1, column=1, sticky="S")
        self.currentTempLabel = tk.Label(self.weatherFrame, text="0°C", font=("Arial", 15), bg="#41c2fa", fg="#ffffff")
        self.currentTempLabel.grid(row=2, column=1, sticky="N")

        self.nextHoursFrame = tk.Frame(self.weatherFrame)
        self.nextHoursFrame.grid(row=4, column=0, columnspan=2)

        self.nextHours = []
        self.nextHoursImagesCanvas = tk.Canvas(self.nextHoursFrame, bg="#bbbbbb", highlightthickness=0, height=35)
        self.nextHoursImages = []
        self.nextHoursTemps = []

        self.nextDaysNameLabels = []
        self.nextDaysTempLabels = []
        self.nextDaysFrameNames = tk.Frame(self.weatherFrame)
        self.nextDaysFrameNames.grid(row=6, column=0, sticky="w")
        self.nextDaysFrameTemps = tk.Frame(self.weatherFrame)
        self.nextDaysFrameTemps.grid(row=6, column=1, sticky="E")

        self.nextHoursImagesCanvas.grid(row=2, column=0, columnspan=100, sticky="ew")
        
        self.additionalDataValueFrame = tk.Frame(self.weatherFrame)
        self.additionalDataNameFrame = tk.Frame(self.weatherFrame)
        self.additionalDataNameFrame.grid(row=8, column=0, sticky="w")
        self.additionalDataValueFrame.grid(row=8, column=1, sticky="e")
        self.additionalDataNameLabels = [tk.Label(self.additionalDataNameFrame, text=self.translator.get("sunrise")), tk.Label(self.additionalDataNameFrame, text=self.translator.get("sunset")), tk.Label(self.additionalDataNameFrame, text=self.translator.get("visibility")), tk.Label(self.additionalDataNameFrame, text=self.translator.get("windSpeed")), tk.Label(self.additionalDataNameFrame, text=self.translator.get("date"))]
        self.additionalDataValueLabels = [tk.Label(self.additionalDataValueFrame), tk.Label(self.additionalDataValueFrame), tk.Label(self.additionalDataValueFrame), tk.Label(self.additionalDataValueFrame), tk.Label(self.additionalDataValueFrame)]

        self.seperator1 = ttk.Separator(self.weatherFrame, orient="horizontal")
        self.seperator1.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.seperator2 = ttk.Separator(self.weatherFrame, orient="horizontal")
        self.seperator2.grid(row=5, column=0, columnspan=2, sticky="ew")

        self.seperator3 = ttk.Separator(self.weatherFrame, orient="horizontal")
        self.seperator3.grid(row=7, column=0, columnspan=2, sticky="ew")

        # CITIES FRAME CONTENT

        self.description = tk.Label(self.citiesFrame, text=self.translator.get("citySelectorDesc").replace("ue", "ü").replace("oe", "ö"), bg="#ffffff")
        self.citySearchLabel = tk.Label(self.citiesFrame, text=self.translator.get("cityEntryDesc"), bg="#ffffff")
        self.citySearch = tk.Entry(self.citiesFrame, bg="#ffffff")
        self.stateSearchLabel = tk.Label(self.citiesFrame, text=self.translator.get("stateEntryDesc"), bg="#ffffff") # Openweathermap takes both code and name
        self.stateSearch = tk.Entry(self.citiesFrame, bg="#ffffff")
        self.countrySearchLabel = tk.Label(self.citiesFrame, text=self.translator.get("countryEntryDesc").replace("ue", "ü"), bg="#ffffff") # If 2 chars long, dont search country code with searchCoutry(), Openweathermap only takes code
        self.countrySearch = tk.Entry(self.citiesFrame, bg="#ffffff")
        self.searchButton = tk.Button(self.citiesFrame, text=self.translator.get("citySearchButton"), bg="#ffffff", command=self.searchCity)
        self.citiesSeparator = ttk.Separator(self.citiesFrame)
        self.searchResultsFrame = tk.Frame(self.citiesFrame, bg="#ffffff")
        self.resultNameFrame = tk.Frame(self.searchResultsFrame, bg="#ffffff")
        self.resultButtonFrame = tk.Frame(self.searchResultsFrame, bg="#ffffff")
        self.citiesSeparator2 = tk.Frame(self.citiesFrame)
        self.savedCitiesFrame = tk.Frame(self.citiesFrame, bg="#ffffff")
        self.savedNameFrame = tk.Frame(self.savedCitiesFrame, bg="#ffffff")
        self.savedButtonsFrame = tk.Frame(self.savedCitiesFrame, bg="#ffffff")

        self.searchResultsFrame.columnconfigure(0, weight=1)
        self.savedCitiesFrame.columnconfigure(0, weight=1)

        self.description.grid(row=0, column=0, columnspan=3)
        self.citySearchLabel.grid(row=1, column=0, sticky="w")
        self.citySearch.grid(row=1, column=1, sticky="e")
        self.stateSearchLabel.grid(row=2, column=0, sticky="w")
        self.stateSearch.grid(row=2, column=1, sticky="e")
        self.countrySearchLabel.grid(row=3, column=0, sticky="w")
        self.countrySearch.grid(row=3, column=1, sticky="e")
        self.searchButton.grid(row=3, column=2, sticky="e")
        self.citiesSeparator.grid(row=4, column=0, columnspan=3, sticky="ew", pady=3)
        self.searchResultsFrame.grid(row=5, column=0, columnspan=3, sticky="nswe")
        self.resultNameFrame.grid(row=0, column=0, sticky="w")
        self.resultButtonFrame.grid(row=0, column=1, sticky="e")
        self.citiesSeparator2.grid(row=6, column=0, columnspan=3, sticky="ew", pady=3)
        self.savedCitiesFrame.grid(row=7, column=0, columnspan=3, sticky="nswe")
        self.savedNameFrame.grid(row=0, column=0, sticky="w")
        self.savedButtonsFrame.grid(row=0, column=1, sticky="e")

        self.searchResultNames = []
        self.searchResultButtons = []
        self.saveResultButtons = []

        self.savedNames = []
        self.viewSavedButtons = []
        self.deleteSavedButtons = []

        self.loadSaved()

        # SETTINGS FRAME CONTENT
        self.settingsFrame.columnconfigure(0, weight=100)

        self.languageLabel = tk.Label(self.settingsFrame, text=self.translator.get("languageSetting"), bg="#ffffff")
        self.languageSetting = tk.IntVar()
        self.languageSetting.set(1)
        self.englishButton = tk.Radiobutton(self.settingsFrame, text="English", variable=self.languageSetting, value=1, bg="#ffffff")
        self.germanButton = tk.Radiobutton(self.settingsFrame, text="Deutsch", variable=self.languageSetting, value=2, bg="#ffffff")
        self.tempUnitLabel = tk.Label(self.settingsFrame, text=self.translator.get("temperatureUnit"), bg="#ffffff")
        self.tempUnitSetting = tk.IntVar()
        self.tempUnitSetting.set(1)
        self.celsiusButton = tk.Radiobutton(self.settingsFrame, text=self.translator.get("celsius"), variable=self.tempUnitSetting, value=1, bg="#ffffff")
        self.fahrenheitButton = tk.Radiobutton(self.settingsFrame, text=self.translator.get("fahrenheit"), variable=self.tempUnitSetting, value=2, bg="#ffffff")
        self.timezoneLabel = tk.Label(self.settingsFrame, text=self.translator.get("timezone"), bg="#ffffff")
        self.timezoneSetting = tk.IntVar()
        self.timezoneSetting.set(1)
        self.yourTimezoneButton = tk.Radiobutton(self.settingsFrame, text=self.translator.get("yourTimezone"), variable=self.timezoneSetting, value=1, bg="#ffffff")
        self.localTimezoneButton = tk.Radiobutton(self.settingsFrame, text=self.translator.get("localTimezone"), variable=self.timezoneSetting, value=2, bg="#ffffff")
        self.saveSettingsButton = tk.Button(self.settingsFrame, text=self.translator.get("saveRestart"), command=self.saveSettings, bg="#ffffff")

        self.languageLabel.grid(row=0, column=0, sticky="nw")
        self.englishButton.grid(row=0, column=1, sticky="ne")
        self.germanButton.grid(row=0, column=2, sticky="ne")
        self.tempUnitLabel.grid(row=1, column=0, sticky="nw")
        self.celsiusButton.grid(row=1, column=1, sticky="ne")
        self.fahrenheitButton.grid(row=1, column=2, sticky="ne")
        self.timezoneLabel.grid(row=2, column=0, sticky="nw")
        self.yourTimezoneButton.grid(row=2, column=1, sticky="ne")
        self.localTimezoneButton.grid(row=2, column=2, sticky="ne")
        self.saveSettingsButton.grid(row=3, column=0, columnspan=3, pady="20")

        if self.settings["language"] == "de":
            self.languageSetting.set(2)
        if self.settings["temperatureUnit"] == "f":
            self.tempUnitSetting.set(2)
        if self.settings["timezone"] == "local":
            self.timezoneSetting.set(2)

        self.drawSidebar()

        self.sideBarCanvas.tag_bind("weatherButton", "<Button-1>", lambda x: self.changeTab(0))
        self.sideBarCanvas.tag_bind("citiesButton", "<Button-1>", lambda x: self.changeTab(1))
        self.sideBarCanvas.tag_bind("settingsButton", "<Button-1>", lambda x: self.changeTab(2))

        self.changeTab(0)
        self.window.resizable(False, False)
        self.window.mainloop()

    def saveSettings(self):
        settings = {}
        if self.languageSetting.get() == 1:
            settings["language"] = "en"
        else:
            settings["language"] = "de"
        if self.tempUnitSetting.get() == 1:
            settings["temperatureUnit"] = "c"
        else:
            settings["temperatureUnit"] = "f"
        if self.timezoneSetting.get() == 1:
            settings["timezone"] = "own"
        else:
            settings["timezone"] = "local"

        file = open("json/settings.json", "w")
        file.write(json.dumps(settings))
        file.close()

        global close
        close = False
        self.window.destroy()
    
    def loadSettings(self):
        file = open("json/settings.json", "r")
        settings = file.readline()
        file.close()
        return json.loads(settings)
    
    def setWeatherData(self):
        currentWeatherData = weather.requestCurrentWeatherData(self.apiKey, self.currentCoords[0], self.currentCoords[1])
        weatherData = weather.requestWeatherData(self.apiKey, self.currentCoords[0], self.currentCoords[1])
        if currentWeatherData == 404 or weatherData == 404:
            messagebox.showinfo(self.translator.get("error"), self.translator.get("weatherNotFound"))
            self.window.destroy()
            exit()

        self.localTime = currentWeatherData[1]
        currentWeatherData = currentWeatherData[0]

        newWeatherData = weather.formatWeatherData(weatherData, self.settings["temperatureUnit"], self)
        if self.settings["temperatureUnit"] == "c":
            self.currentTempLabel["text"] = str(uc.kelvinToCelsius(currentWeatherData["main"]["temp"])) + "°C"
        else:
            self.currentTempLabel["text"] = str(uc.kelvinToFahrenheit(currentWeatherData["main"]["temp"])) + "°F"

        data = weather.getWeather(self, currentWeatherData["weather"][0]["main"], currentWeatherData["weather"][0]["description"])

        self.placeName["bg"] = data[3]
        self.placeName["text"] = weatherData["city"]["name"] + ", " + weatherData["city"]["country"]

        self.currentWeatherLabel["text"] = data[2]
        self.currentWeatherImg.itemconfig(self.weatherImg, image=data[0])

        self.sideBarCanvas.itemconfig(self.chooseCircle, fill=data[3])
        self.window["bg"] = data[3]
        self.currentWeatherImg["bg"] = data[3]
        self.currentWeatherLabel["bg"] = data[3]
        self.currentTempLabel["bg"] = data[3]
        self.weatherFrame["bg"] = data[3]
        self.nextHoursImagesCanvas["bg"] = data[3]
        self.nextHoursFrame["bg"] = data[3]
        self.nextDaysFrameNames["bg"] = data[3]
        self.additionalDataNameFrame["bg"] = data[3]
        self.additionalDataValueFrame["bg"] = data[3]

        for lbl in range(len(self.nextHours)):
            self.nextHours[-1].grid_forget()
            self.nextHoursImagesCanvas.delete(self.nextHoursImages[-1])
            self.nextHoursTemps[-1].grid_forget()

            self.nextHours.pop(-1)
            self.nextHoursImages.pop(-1)
            self.nextHoursTemps.pop(-1)
        
        for lbl in range(len(self.nextDaysNameLabels)):
            self.nextDaysNameLabels[-1].grid_forget()
            self.nextDaysTempLabels[-1].grid_forget()

            self.nextDaysNameLabels.pop(-1)
            self.nextDaysTempLabels.pop(-1)

        i=0
        for list in newWeatherData:
            if i <= 14:
                if self.settings["timezone"] == "own":
                    self.nextHours.append(tk.Label(self.nextHoursFrame, text=datetime.datetime.fromtimestamp(int(list[4])).strftime("%H:%M"), bg=data[3], fg="#ffffff"))
                else:
                    self.nextHours.append(tk.Label(self.nextHoursFrame, text=datetime.datetime.utcfromtimestamp(self.getLocalTime(int(list[4]))).strftime("%H:%M"), bg=data[3], fg="#ffffff"))
                self.nextHoursImages.append(self.nextHoursImagesCanvas.create_image(i * 33, 0, image=list[5], anchor="nw"))
                if self.settings["temperatureUnit"] == "c":
                    self.nextHoursTemps.append(tk.Label(self.nextHoursFrame, text=(str(list[3]) + "°C"), fg="#ffffff", bg=data[3]))
                else:
                    self.nextHoursTemps.append(tk.Label(self.nextHoursFrame, text=(str(list[3]) + "°F"), fg="#ffffff", bg=data[3]))
            i += 1
        
        nextDaysWeatherData = self.getDaysWeather(newWeatherData)
        for i in newWeatherData[::8]:

            #self.nextDaysNameLabels.append(tk.Label(self.nextDaysFrameNames, text=datetime.datetime.fromtimestamp(i[4]).strftime("%A"), bg=data[3], fg="#ffffff"))
            self.nextDaysNameLabels.append(tk.Label(self.nextDaysFrameNames, text=self.getWeekday(datetime.datetime.fromtimestamp(i[4]).weekday()), bg=data[3], fg="#ffffff"))
            self.nextDaysTempLabels.append(tk.Label(self.nextDaysFrameTemps, bg=data[3], fg="#ffffff"))
        
        for lbl in range(len(self.nextDaysNameLabels)):
            self.nextDaysNameLabels[lbl].grid(row=lbl, column=0, sticky="W")
            if self.settings["temperatureUnit"] == "c":
                self.nextDaysTempLabels[lbl]["text"] = (str(uc.kelvinToCelsius(nextDaysWeatherData[lbl][1])) + "°C")
            else:
                self.nextDaysTempLabels[lbl]["text"] = (str(uc.kelvinToFahrenheit(nextDaysWeatherData[lbl][1])) + "°F")
            self.nextDaysTempLabels[lbl].grid(row=lbl, column=1, sticky="E")

        for lbl in range(len(self.nextHours)):
            self.nextHours[lbl].grid(row=0, column=lbl)
            self.nextHoursTemps[lbl].grid(row=3, column=lbl)
        
        for lbl in range(len(self.additionalDataNameLabels)):
            self.additionalDataNameLabels[lbl].grid(row=lbl, column=0, sticky="W")
            self.additionalDataNameLabels[lbl]["bg"] = data[3]
            self.additionalDataNameLabels[lbl]["fg"] = "#ffffff"

            self.additionalDataValueLabels[lbl].grid(row=lbl, column=1, sticky="E")
            self.additionalDataValueLabels[lbl]["bg"] = data[3]
            self.additionalDataValueLabels[lbl]["fg"] = "#ffffff"
        
        if self.settings["timezone"] == "own":
            self.additionalDataValueLabels[0]["text"] = datetime.datetime.fromtimestamp(currentWeatherData["sys"]["sunrise"]).strftime('%H:%M')
            self.additionalDataValueLabels[1]["text"] = datetime.datetime.fromtimestamp(currentWeatherData["sys"]["sunset"]).strftime('%H:%M')
            self.additionalDataValueLabels[4]["text"] = datetime.datetime.fromtimestamp(currentWeatherData["dt"]).strftime("%H:%M, %d.%m")
        else:
            self.additionalDataValueLabels[0]["text"] = datetime.datetime.utcfromtimestamp(self.getLocalTime(currentWeatherData["sys"]["sunrise"])).strftime('%H:%M')
            self.additionalDataValueLabels[1]["text"] = datetime.datetime.utcfromtimestamp(self.getLocalTime(currentWeatherData["sys"]["sunset"])).strftime('%H:%M')
            self.additionalDataValueLabels[4]["text"] = datetime.datetime.utcfromtimestamp(self.getLocalTime(currentWeatherData["dt"])).strftime("%H:%M, %d.%m")
        self.additionalDataValueLabels[2]["text"] = str(round(currentWeatherData["visibility"] / 1000, 1)) + " km"
        self.additionalDataValueLabels[3]["text"] = str(currentWeatherData["wind"]["speed"]) + " m/s"
        

        if currentWeatherData["visibility"] == 10000:
            self.additionalDataValueLabels[2]["text"] = "10+ km"
        
        self.window.update()
        self.window.size()
        self.window.geometry(str(self.window.winfo_width()) + "x" + str(self.window.winfo_height()))

    def getWeekday(self, weekday):
        if weekday == 0:
            return self.translator.get("monday")
        elif weekday == 1:
            return self.translator.get("tuesday")
        elif weekday == 2:
            return self.translator.get("wednesday")
        elif weekday == 3:
            return self.translator.get("thursday")
        elif weekday == 4:
            return self.translator.get("friday")
        elif weekday == 5:
            return self.translator.get("saturday")
        elif weekday == 6:
            return self.translator.get("sunday")
    
    def getDaysWeather(self, weatherData):
        day = datetime.datetime.fromtimestamp(weatherData[0][4]).weekday()
        output = []
        tempMin = []
        tempMax = []
        for i in weatherData:
            if day == datetime.datetime.fromtimestamp(i[4]).weekday():
                tempMin.append(i[6])
                tempMax.append(i[7])
            else:
                output.append([tempMin, tempMax])
                day = datetime.datetime.fromtimestamp(i[4]).weekday()
                tempMin = []
                tempMax = []
                tempMin.append(i[6])
                tempMax.append(i[7])
        
        for i in range(len(output)):
            output[i][0] = max(output[i][0])
            output[i][1] = max(output[i][1])

        return output
    
    def getLocalTime(self, time):
        return time + self.localTime

    def changeTab(self, tabId):
        if tabId != self.currentFrame and tabId == 0:
            self.setWeatherData()
        moveCircleThread = Thread(target=lambda x=tabId: self.moveChooseCircle(x))
        moveCircleThread.start()
        for symbol in range(len(self.sideBarSymbols)): 
            if symbol < tabId:
                self.sideBarCanvas.coords(self.sideBarSymbols[symbol], self.symbolPositions[symbol][0][0], self.symbolPositions[symbol][0][1])
            elif symbol == tabId:
                self.sideBarCanvas.coords(self.sideBarSymbols[symbol], self.symbolPositions[symbol][1][0], self.symbolPositions[symbol][1][1])
            elif symbol > tabId:
                self.sideBarCanvas.coords(self.sideBarSymbols[symbol], self.symbolPositions[symbol][2][0], self.symbolPositions[symbol][2][1])
        if self.currentFrame != tabId:
            if self.currentFrame == 0:
                self.weatherFrame.grid_forget()
            elif self.currentFrame == 1:
                self.citiesFrame.grid_forget()
            elif self.currentFrame == 2:
                self.settingsFrame.grid_forget()

            if tabId == 0:
                self.weatherFrame.grid(row=0, column=1, sticky="NSWE")
            elif tabId == 1:
                self.citiesFrame.grid(row=0, column=1, sticky="NSWE")
                self.setBg("#ffffff")
            elif tabId == 2:
                self.settingsFrame.grid(row=0, column=1, sticky="NSWE", padx=(0, 65))
                self.setBg("#ffffff")

            self.currentFrame = tabId
            
    def moveChooseCircle(self, tabId): # Use in thread. Otherwise program freezes
        speed = 4
        lastFrameTime = time.time()
        startPosition = self.sideBarCanvas.coords(self.chooseCircle)
        currentPosition = startPosition
        endPosition = self.chooseCirclePositions[tabId]
        speedMultiplier = abs(startPosition[1]-endPosition[1]) * speed
        breakLoop = False
        while True:
            currentTime = time.time()
            delta = currentTime - lastFrameTime # Multiply an animation by delta to make sure that the speed is consistent
            lastFrameTime = currentTime
            if startPosition[1] > endPosition[1]:
                if currentPosition[1] - delta * speedMultiplier > endPosition[1]:
                    currentPosition = [currentPosition[0], currentPosition[1] - delta * speedMultiplier , currentPosition[2], currentPosition[3] - delta * speedMultiplier]
                else:
                    currentPosition = endPosition
                    breakLoop = True
            else:
                if currentPosition[1] + delta * speedMultiplier < endPosition[1]:
                    currentPosition = [currentPosition[0], currentPosition[1] + delta * speedMultiplier , currentPosition[2], currentPosition[3] + delta * speedMultiplier]
                else:
                    currentPosition = endPosition
                    breakLoop = True
            
            self.sideBarCanvas.coords(self.chooseCircle, currentPosition[0], currentPosition[1], currentPosition[2], currentPosition[3])
            if breakLoop == True:
                break
    
    def searchCity(self):
        city = self.citySearch.get()
        state = self.stateSearch.get()
        country = self.countrySearch.get()

        if city == "":
            return "noCity"
        if state == "":
            state = "none"
        if country == "":
            country = "none"

        cities = weather.requestCoordinates(self.apiKey, city, state, country)

        for city in range(len(self.searchResultNames)):
            self.searchResultNames[-1].grid_forget()
            self.searchResultButtons[-1].grid_forget()
            self.saveResultButtons[-1].grid_forget()

            self.searchResultNames.pop(-1)
            self.searchResultButtons.pop(-1)
            self.saveResultButtons.pop(-1)

        if cities != [] and cities != "error":
            for city in cities:
                self.searchResultNames.append(tk.Label(self.resultNameFrame, text=city[0] + ", " + city[3] + ", " + weather.getCountryName(city[4]), pady=4, bg="#ffffff"))
                self.searchResultNames[-1].grid(row=len(self.searchResultNames) - 1, column=0, sticky="w")

                self.searchResultButtons.append(tk.Button(self.resultButtonFrame, text=self.translator.get("cityViewButton"), bg="#ffffff", command=lambda lat=str(city[1]), lon=str(city[2]): self.viewWeather(lat, lon)))
                self.searchResultButtons[-1].grid(row=len(self.searchResultNames) - 1, column=1, sticky="e")

                self.saveResultButtons.append(tk.Button(self.resultButtonFrame, text=self.translator.get("citySaveButton"), bg="#ffffff", command=lambda name=city[0] + ", " + city[4], lat=city[1], lon=city[2]: self.save(name, lat, lon)))
                self.saveResultButtons[-1].grid(row=len(self.searchResultButtons) - 1, column=0, sticky="e")
        else:
            messagebox.showinfo(self.translator.get("error"), self.translator.get("cityNotFound"))
    
    def viewWeather(self, lat, lon):
        self.currentCoords = [lat, lon]
        self.changeTab(0)
    
    def save(self, name, lat, lon):
        savedList = self.loadSaved()
        
        if not any(name in sublist for sublist in savedList):
            if len(savedList) < 12:
                savedList.append([name, lat, lon])
                file = open("json/savedCities.json", "w")
                file.write(json.dumps(savedList))
                file.close()
                self.loadSaved()
            else:
                messagebox.showinfo(self.translator.get("error"), message=self.translator.get("maxCityAmount").replace("ae", "ä"))
        else:
            messagebox.showinfo(title=self.translator.get("error"), message=self.translator.get("cityAlreadySaved"))
    
    def deleteSaved(self, index):
        savedList = self.loadSaved()
        savedList.pop(index)
        file = open("json/savedCities.json", "w")
        file.write(json.dumps(savedList))
        file.close()
        self.loadSaved()
    
    def loadSaved(self):
        if exists("json/savedCities.json"):
            file = open("json/savedCities.json", "r")
            savedList = json.loads(file.readline())
            file.close()
        else:
            savedList = []
        
        for city in range(len(self.savedNames)):
            self.savedNames[city].grid_forget()
            self.viewSavedButtons[city].grid_forget()
            self.deleteSavedButtons[city].grid_forget()

        self.savedNames = []
        self.viewSavedButtons = []
        self.deleteSavedButtons = []

        if savedList != []:
            i = 0
            for city in savedList:
                self.savedNames.append(tk.Label(self.savedNameFrame, text=city[0], bg="#ffffff", pady=3))
                self.viewSavedButtons.append(tk.Button(self.savedButtonsFrame, text=self.translator.get("cityViewButton"), bg="#ffffff", command=lambda lat=str(city[1]), lon=str(city[2]): self.viewWeather(lat, lon)))
                self.deleteSavedButtons.append(tk.Button(self.savedButtonsFrame, text=self.translator.get("cityDeleteButton").replace("oe", "ö"), bg="#ffffff", command=lambda index=i: self.deleteSaved(index)))

                self.savedNames[-1].grid(row=len(self.savedNames), column=0, sticky="w")
                self.deleteSavedButtons[-1].grid(row=len(self.savedNames), column=0, sticky="e")
                self.viewSavedButtons[-1].grid(row=len(self.savedNames), column=1, sticky="e")
                i += 1

        return savedList
    
    def setBg(self, color):
        self.window["bg"] = color
        self.citiesFrame["bg"] = color
        self.settingsFrame["bg"] = color
        self.sideBarCanvas.itemconfig(self.chooseCircle, fill=color)
    
    def drawSidebar(self):
        self.window.weatherImage = tk.PhotoImage(file="img/weatherSymbol.png").subsample(13)
        self.window.mapIcon = tk.PhotoImage(file="img/mapIcon.png").subsample(13)
        self.window.settingsIcon = tk.PhotoImage(file="img/settingsIcon.png").subsample(13)
        self.sideBarSymbols.append(self.sideBarCanvas.create_image(5, 5, image=self.window.weatherImage, anchor="nw", tag="weatherButton"))
        self.sideBarSymbols.append(self.sideBarCanvas.create_image(5, 60, image=self.window.mapIcon, anchor="nw", tag="citiesButton"))
        self.sideBarSymbols.append(self.sideBarCanvas.create_image(5, 200, image=self.window.settingsIcon, anchor="nw", tag="settingsButton"))
            
if __name__ == "__main__":
    while close == False:
        close = True
        program = programWindow("b1c8a5cea60f17f305ee2d9e3305af25")