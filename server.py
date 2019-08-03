from flask import Flask, render_template, redirect, request, session
import settings
import urllib.request
import json, sys, time, datetime
import urllib.parse
import dateutil.parser
from urllib.error import URLError, HTTPError


app = Flask(__name__)
app.secret_key = settings.SECRET_KEY
accuKey = settings.ACCU_KEY


@app.route('/')
def index():
    session.clear()
    return render_template ('index.html')

@app.route('/input')
def input():
    zipCode = request.args['zipInput']
    session['zipCode'] = zipCode
    textInput = request.args['cityInput']
    session['textInput'] = textInput
    print('printing session text input from input function ' + session['textInput'] )
    if zipCode:
        return redirect('/zipLocKey')
    if textInput:
        return redirect('/textLocKey')

@app.route('/textLocKey')
def getTextLocKey():
    lookUpText = session['textInput']
    lookUpText = urllib.parse.quote(lookUpText)
    
    searchUrl = "http://dataservice.accuweather.com/locations/v1/cities/US/search?apikey="  + accuKey + "&q=" + lookUpText
    print('printing search URL from textLocKey function' + searchUrl)
    try:
        with urllib.request.urlopen(searchUrl) as url:
            data = json.loads(url.read().decode())
        print(url.getheaders())
        print(url.getcode())
        print('type of data: ' + str(type(data)))
        print(len(data))
        if url.getcode() == 200:
            if not data or len(data) == 0:
                session['error'] = 500
                return render_template ('index.html', errNum=session['error'])
            if data:
                locationKey = data[0]['Key']
                cityName = data[0]['LocalizedName']
                stateName = data[0]['AdministrativeArea']['LocalizedName']
                session['locationKey'] = locationKey
                session['cityName'] = cityName
                session['stateName'] = stateName
                print(locationKey)
                return redirect('/results')
    except urllib.error.HTTPError as e:
        if e.code == 503:
            session['error'] = 503
            return render_template ('index.html', errNum=session['error'])
        if e.code > 400:
            error = url.getcode()
            session['error'] = error
            return render_template ('index.html', errNum=session['error'])
        print('Error code: ', e.code)
    

@app.route('/zipLocKey', methods=['GET'])
def getLocationKey():
    zipCode = session['zipCode']
    searchUrl = "http://dataservice.accuweather.com/locations/v1/postalcodes/US/search?apikey=" + accuKey + "&q=" + zipCode
    print(searchUrl)

    try:
        with urllib.request.urlopen(searchUrl) as url:
            data = json.loads(url.read().decode())
        print(url.getheaders())
        print(url.getcode())
        print('type of data: ' + str(type(data)))
        print(len(data))
        if url.getcode() == 200:
            if not data or len(data) == 0:
                session['error'] = 500
                return render_template ('index.html', errNum=session['error'])
            if data:
                locationKey = data[0]['Key']
                cityName = data[0]['LocalizedName']
                stateName = data[0]['AdministrativeArea']['LocalizedName']
                session['locationKey'] = locationKey
                session['cityName'] = cityName
                session['stateName'] = stateName
                print(locationKey)
                return redirect('/results')
    except urllib.error.HTTPError as e:
        if e.code == 503:
            session['error'] = 503
            return render_template ('index.html', errNum=session['error'])
        if e.code > 400:
            error = url.getcode()
            session['error'] = error
            return render_template ('index.html', errNum=session['error'])
        print('Error code: ', e.code)

    
#results of search
@app.route('/results')
def results():
    searchUrl = 'http://dataservice.accuweather.com/forecasts/v1/daily/1day/' + session['locationKey'] + "?&apikey=" + accuKey + '&details=true'
    try:
        with urllib.request.urlopen(searchUrl) as url:
            data = json.loads(url.read().decode())    
        date = data['DailyForecasts'][0]['Date']
        date2 = dateutil.parser.parse(date)
        date3 = date2.strftime('%B'+" " + '%d' + ', ' + '%Y' + " " + '%I:%M%p')
        airPollen = data['DailyForecasts'][0]["AirAndPollen"]
        print(date2)
        print(json.dumps(airPollen, indent=4, sort_keys=True))
        if data:
            found=True
            return render_template ('index.html', found=found, data=airPollen, date=date3, cityName=session['cityName'], stateName=session['stateName'])

    except urllib.error.HTTPError as e:
        if e.code == 503:
            session['error'] = 503
            return render_template ('index.html', errNum=session['error'])
        if e.code > 400:
            error = url.getcode()
            session['error'] = error
            return render_template ('index.html', errNum=session['error'])
        print('Error code: ', e.code)


# #use this RESULTS for testing
# @app.route('/results')
# def results():
#     with open('boston.txt', 'r') as handle:
#         data = json.load(handle)
#     date = data['DailyForecasts'][0]['Date']
#     date2 = dateutil.parser.parse(date)
#     date3 = date2.strftime('%B'+" " + '%d' + ', ' + '%Y' + " " + '%I:%M%p')


#     # date = data['DailyForecasts'][0]['Date']
#     # # datetimestr = '2019-07-28 20:00:00-04:00'
#     # date2 = datetime.datetime.strptime(datetimestr, '%Y-%m-%d %H:%M:%S%z')
#     # date2 = date2.strftime('%B'+ " " + '%d' + ', ' + '%Y' + " " + '%I:%M%p')

#     airPollen = data["DailyForecasts"][0]["AirAndPollen"]
#     # airPollen=data
#     print(json.dumps(airPollen, indent=4, sort_keys=True))
#     if data:
#         found=True
#     return render_template ('index.html', found=found, data=airPollen, date=date3, cityName="Detroit", stateName="Michigan")


if __name__=="__main__":
    app.run()
 