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
    
    try:
        with urllib.request.urlopen(searchUrl) as url:
            data = json.loads(url.read().decode())
        
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
                
                return redirect('/results')
    except urllib.error.HTTPError as e:
        if e.code: 
            session['error'] = e.code
            return render_template ('index.html', errNum=session['error'])

    

@app.route('/zipLocKey', methods=['GET'])
def getLocationKey():
    zipCode = session['zipCode']
    searchUrl = "http://dataservice.accuweather.com/locations/v1/postalcodes/US/search?apikey=" + accuKey + "&q=" + zipCode
    
    try:
        with urllib.request.urlopen(searchUrl) as url:
            data = json.loads(url.read().decode())
        
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
                
                return redirect('/results')
    except urllib.error.HTTPError as e:
        if e.code: 
            session['error'] = e.code
            return render_template ('index.html', errNum=session['error'])


    
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
        print(json.dumps(data, indent=4, sort_keys=True))
        print(json.dumps(airPollen, indent=4, sort_keys=True))
        if data:
            found=True
            return render_template ('index.html', found=found, data=airPollen, date=date3, cityName=session['cityName'], stateName=session['stateName'])

    except urllib.error.HTTPError as e:
        if e.code: 
            session['error'] = e.code
            return render_template ('index.html', errNum=session['error'])




if __name__=="__main__":
    app.run()
 