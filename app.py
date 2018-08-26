from flask import Flask
from flask import render_template
import geocoder
import requests
import requests_cache
from dateutil.parser import parse

app = Flask(__name__)

# Weather API URLs
api_endpoint = 'https://api.weather.gov'
api_forecast_week = api_endpoint + '/points/{0},{1}/forecast'
api_forecast_today = api_endpoint + '/points/{0},{1}/forecast/hourly'
# Requests cache config
requests_cache.install_cache('nws_cache', backend='sqlite', expire_after=180000)


@app.template_filter('datetimeformat')
def datetimeformat(value, format='%H:%M / %d-%m-%Y'):
    return parse(value).strftime(format)


@app.route('/')
@app.route('/forecast/week')
def forecast_week():
    # Get user location g.lat g.lng | test with Mountain View
    g = geocoder.ip('8.8.8.8' if app.config['ENV'] == 'development' else 'me')
    # Call weather API
    r = requests.get(api_forecast_week.format(str(g.lat), str(g.lng)))
    # We have a response
    if r.status_code == 200:
        return render_template(
            'forecast_week.html',
            country=g.country,
            city=g.city,
            now=r.json()['properties']['periods'][0],
            is_daytime=r.json()['properties']['periods'][0]['isDaytime'],
            periods=r.json()['properties']['periods'][1:])
    else:
        return render_template(
            'error.html',
            error=r.json()
        )


@app.route('/forecast/today')
def forecast_today():
    # Get user location g.lat g.lng | test with Mountain View
    g = geocoder.ip('8.8.8.8' if app.config['ENV'] == 'development' else 'me')
    # Call weather API
    r = requests.get(api_forecast_today.format(str(g.lat), str(g.lng)))
    # We have a response
    if r.status_code == 200:
        return render_template(
            'forecast_today.html',
            country=g.country,
            city=g.city,
            now=r.json()['properties']['periods'][0],
            is_daytime=r.json()['properties']['periods'][0]['isDaytime'],
            periods=r.json()['properties']['periods'][1:])
    else:
        return render_template(
            'error.html',
            error=r.json()
        )


@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


if __name__ == '__main__':
    app.run()