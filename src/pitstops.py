import numpy as np  # linear algebra
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px


#Read data from multiple CSV
circuits = pd.read_csv('../data/circuits.csv', index_col=0, na_values=r'\N')
constructorResults = pd.read_csv('../data/constructor_results.csv', index_col=0, na_values=r'\N')
constructors = pd.read_csv('../data/constructors.csv', index_col=0, na_values=r'\N')
constructorStandings = pd.read_csv('../data/constructor_standings.csv', index_col=0, na_values=r'\N')
drivers = pd.read_csv('../data/drivers.csv', index_col=0, na_values=r'\N')
driverStandings = pd.read_csv('../data/driver_standings.csv', index_col=0, na_values=r'\N')
lapTimes = pd.read_csv('../data/lap_times.csv')
pitStops = pd.read_csv('../data/pit_stops.csv')
qualifying = pd.read_csv('../data/qualifying.csv', index_col=0, na_values=r'\N')
races = pd.read_csv('../data/races.csv', na_values=r'\N')
results = pd.read_csv('../data/results.csv', index_col=0, na_values=r'\N')
seasons = pd.read_csv('../data/seasons.csv', index_col=0, na_values=r'\N')
status = pd.read_csv('../data/status.csv', index_col=0, na_values=r'\N')

constructor_color_map = {
    'Toro Rosso': '#0000FF',
    'Mercedes': '#6CD3BF',
    'Red Bull': '#1E5BC6',
    'Ferrari': '#ED1C24',
    'Williams': '#37BEDD',
    'Force India': '#FF80C7',
    'Virgin': '#c82e37',
    'Renault': '#FFD800',
    'McLaren': '#F58020',
    'Sauber': '#006EFF',
    'Lotus': '#FFB800',
    'HRT': '#b2945e',
    'Caterham': '#0b361f',
    'Lotus F1': '#FFB800',
    'Marussia': '#6E0000',
    'Manor Marussia': '#6E0000',
    'Haas F1 Team': '#B6BABD',
    'Racing Point': '#F596C8',
    'Aston Martin': '#2D826D',
    'Alfa Romeo': '#B12039',
    'AlphaTauri': '#4E7C9B',
    'Alpine F1 Team': '#2293D1'
}

# Post-reading formatting
drivers = drivers.rename(columns={'nationality': 'driverNationality', 'url': 'driverUrl'})
drivers['driverName'] = drivers['forename'] + ' ' + drivers['surname']

constructors = constructors.rename(
    columns={'name': 'constructorName', 'nationality': 'constructorNationality', 'url': 'constructorUrl'})

races.set_index('raceId', inplace=True)
races['date'] = races['date'].apply(lambda x: dt.datetime.strptime(x, '%Y-%m-%d'))

pitStops = pitStops.rename(columns={'time': 'pitTime'})
pitStops['seconds'] = pitStops['milliseconds'].apply(lambda x: x / 1000)

results['seconds'] = results['milliseconds'].apply(lambda x: x / 1000)

circuits = circuits.rename(
    columns={'name': 'circuitName', 'location': 'circuitLocation', 'country': 'circuitCountry', 'url': 'circuitUrl'})


newResults = pd.merge(results, races, left_on='raceId', right_index=True, how='left')
newResults = pd.merge(newResults, constructors, left_on='constructorId', right_index=True, how='left')
newResults = pd.merge(newResults, drivers, left_on='driverId', right_index=True, how='left')
newResults = pd.merge(newResults,circuits,left_on='circuitId',right_index=True,how='left')

newPitStops = pd.merge(pitStops, races, left_on='raceId', right_index=True, how='left')
newPitStops = pd.merge(newPitStops,
                       newResults[['raceId', 'driverId', 'driverName', 'constructorId', 'constructorName']],
                       left_on=['raceId', 'driverId'], right_on=['raceId', 'driverId'])

year = 2021
fig = plt.box(newPitStops[(newPitStops['seconds'] < 50) & (newPitStops['year'] == year)].groupby(
    by=['raceId', 'name', 'date', 'constructorName']).mean().reset_index().sort_values(by='seconds', ascending=True),
             x='constructorName',
             y='seconds',
             color='constructorName',
             color_discrete_map=constructor_color_map,
             )
fig.update_layout(
    title_text=f'Pit Stop Durations by Constructor for {year} Season',
)
fig.show()


