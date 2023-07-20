import pandas as pd
import datetime as dt
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns
import matplotlib.pyplot as plt

# Lecture des CSV
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

# Couleur des constructeurs
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

# Formattage de certaines colonnes

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

# Dataframe central sur lequel nous allons nous appuyer
bigDF = pd.merge(results, races, left_on='raceId', right_index=True, how='left')
bigDF = pd.merge(bigDF, constructors, left_on='constructorId', right_index=True, how='left')
bigDF = pd.merge(bigDF, drivers, left_on='driverId', right_index=True, how='left')
bigDF = pd.merge(bigDF, circuits, left_on='circuitId', right_index=True, how='left')
bigDF

# Matrice de corrélation pour voir si nous pouvons trouver des hypothèses avec
dfCorr = bigDF[
    ['grid', 'position', 'points', 'rank', 'milliseconds', 'statusId', 'year', 'round', 'name', 'date', 'sprint_time',
     'constructorName', 'constructorNationality', 'driverName', 'driverNationality']]
plt.figure(figsize=(20, 20))
sns.heatmap(dfCorr.corr(method='pearson'), annot=True)
plt.show()

# _______________________________________________________________________Focus sur Lewis Hamilton et ses écuries_______________________________________________________________________#

driver = 'Lewis Hamilton'
startYear = 2005
endYear = 2020
constructorsFocused = ['McLaren', 'Mercedes']

# Calcul des victoires par année de l'écurie Mercedes
dfConstructorsFocused = bigDF[
    (bigDF['constructorName'].isin(constructorsFocused)) & (bigDF['year'] >= startYear) & (bigDF['year'] <= endYear) & (
            bigDF['position'] == 1)]

dfConstructorsFocused = dfConstructorsFocused[['constructorName', 'year', 'driverName']]
dfConstructorsFocusedV2 = dfConstructorsFocused.groupby(['year', 'constructorName']).size().reset_index(
    name='winCounts')

dfMercedes = dfConstructorsFocusedV2[(dfConstructorsFocusedV2['constructorName'] == 'Mercedes')]
dfMcLaren = dfConstructorsFocusedV2[(dfConstructorsFocusedV2['constructorName'] == 'McLaren')]
dfConstructorsFocusedV2

# On remarque une augmentation des victoires à partir de 2012
fig = px.line(dfMercedes, x='year', y='winCounts', color='constructorName', color_discrete_map=constructor_color_map,
              title=f'Victoires de Mercedes {startYear} à {endYear}')
fig.update_yaxes(title_text='Nombre de victoires')
fig.update_xaxes(title_text='Année')
fig.show()

# Calcul des victoires de Lewis Hamilton par année
dfLewis = dfConstructorsFocused[(dfConstructorsFocused['driverName'] == driver)]
dfLewis = dfLewis.groupby(['year', 'driverName']).size().reset_index(name='winsCount')
dfLewis

# Impact de Lewis Hamilton sur ses équipes durant sa carrière
fig = px.bar(dfConstructorsFocusedV2, x='year', y='winCounts', color='constructorName',
             color_discrete_map=constructor_color_map, title='Impact de Lewis Hamilton sur ses équipes')
fig.update_yaxes(nticks=int(dfConstructorsFocusedV2['winCounts'].max()))
fig.add_scatter(x=dfLewis['year'], y=dfLewis['winsCount'], mode='lines', line=dict(color='red'), name='Hamilton')
fig.update_xaxes(dtick='M1')
fig.show()

# _______________________________________________________________________Corrélation nombre de pilotes et longévité d'une carrière de pilote_______________________________________________________________________#


# On remarque qu'il y'a de moins en moins de pilotes par décennie
countingPilots = bigDF[['driverName', 'year']]
countingPilots['decade'] = countingPilots['year'].apply(lambda x: (x // 10) * 10)
countingPilots = countingPilots.drop_duplicates().groupby('decade')['driverName'].nunique().reset_index()
countingPilots

# Analyse du nombre de pilotes par décennies
fig = px.line(countingPilots, x="decade", y='driverName', title='Nombre de pilotes par décennies de 1950 à 2020',
              width=1500)

fig.update_yaxes(title_text='Nombre de pilotes')
fig.update_xaxes(title_text='Décennie')

fig.show()

chosenYears = [1950, 1960, 1970, 1980, 1990, 2000, 2010, 2020]

# Calcul de la longevité moyenne du paddock lors des années choisies
dfLongevity = bigDF[['driverName', 'date', 'year']]
dfLongevity['date'] = pd.to_datetime(dfLongevity['date'])

tmp = dfLongevity.groupby('driverName')['year'].agg(['min'])

dfLongevity = dfLongevity.merge(tmp, left_on='driverName', right_index=True)
dfLongevity['longevity'] = (dfLongevity['year'] - dfLongevity['min'])

dfLongevity.drop_duplicates(subset=['driverName', 'year'], inplace=True)
dfLongevity

dfLongevity = dfLongevity[(dfLongevity['year'].isin(chosenYears))]
dfLongevity = dfLongevity.groupby('year')['longevity'].mean().reset_index()
dfLongevity

# Evolution du nombre de pilotes suivant la longévité moyenne du paddock
bar_trace = go.Bar(x=countingPilots['decade'], y=countingPilots['driverName'], name='Nombre de pilotes')
line_trace2 = go.Scatter(x=dfLongevity['year'], y=dfLongevity['longevity'], mode='lines', name='Longevité moyenne',
                         yaxis='y2')

fig = go.Figure(data=[bar_trace, line_trace2])

fig.update_layout(
    title="Evolution du nombre de pilotes suivant la longévité moyenne du paddock",
    yaxis2=dict(
        title='Age',
        overlaying='y',
        side='right',

    ),
    yaxis=dict(title='Nombre pilotes'),
    xaxis=dict(title='Décennie / Année')
)

fig.show()

# _______________________________________________________________________Corrélation entre l'arrivée des courses Sprint et les dommages sur les monoplaces_______________________________________________________________________#

# Les statuts étant considérés comme des accidents ou des dommages sur les voitures
statusFocused = [3, 4, 20, 29, 31, 41, 44, 47, 54, 56, 59, 66, 68, 73, 75, 76, 82, 95, 104, 107, 130, 137]

# Nombre d'accidents et de dommages par an et par écurie
statusDF = pd.merge(bigDF, status, left_index=True, right_index=True, how='left')
statusDFrom2012 = statusDF[(statusDF['statusId'].isin(statusFocused)) & (statusDF['year'] >= 2012)]
statusDFrom2012 = statusDFrom2012[['constructorName', 'year', 'statusId']]

statusDFByYear = statusDFrom2012.groupby("year").agg({'statusId': 'size'}).reset_index()

fig = px.bar(statusDFByYear,
             x='year',
             y='statusId',
             title='Nombre de dommages et accidents par saison avant et après arrivée des courses sprint'
             )
fig.update_yaxes(title_text='Accidents / Dommages')
fig.update_xaxes(title_text='Année', nticks=20)
fig.add_shape(
    type='line',
    x0=2020 - 0.5, y0=0,
    x1=2022 + 0.5, y1=0,
    line=dict(color='Red', width=3)
)
fig.add_annotation(
    x=2020, y=0,
    text="Arrivée des courses Sprint",
    showarrow=True,
    arrowhead=1,
    ax=0,
    ay=-300,
    font=dict(
        size=17
    ),
    bgcolor='red',

)
fig.show()

# _______________________________________________________________________Analyse sur les mauvaises performances de Ferrari_______________________________________________________________________#

# On remarque que le nombre de victoires par an diminue ces dernières années chez Ferrari
winByFerrari = bigDF[(bigDF['position'] == 1) & (bigDF['constructorName'] == 'Ferrari') & (bigDF['year'] >= 1990)]
winByFerrari = winByFerrari[['year', 'constructorName']]
winByFerrari = winByFerrari.groupby('year').agg(count=('year', 'size'),
                                                constructor=('constructorName', 'first')).reset_index()

fig = px.bar(winByFerrari, x='year', y='count', color='constructor', color_discrete_map=constructor_color_map,
             title='Victoires de Ferrari par année de 1990 à 2022', width=1500)
fig.update_yaxes(title_text='Nombre de victoires')
fig.update_xaxes(title_text='Années', nticks=40)
fig.show()

# Analyse des accidents et dommages sur les monoplaces Ferrari depuis 1990
statusDFByYearFerrari = statusDF[(statusDF['constructorName'] == 'Ferrari') & (statusDF['year'] >= 1990)]
statusDFByYearFerrari = statusDFByYearFerrari.groupby('year').agg(
    {'statusId': 'size', 'constructorName': 'first'}).reset_index()

fig = px.line(statusDFByYearFerrari, x='year', y='statusId', color='constructorName',
              color_discrete_map=constructor_color_map, title='Nombre de dommages et accidents par saison chez Ferrari')
fig.update_yaxes(title_text='Dommages / Accidents')
fig.update_xaxes(title_text='Années', nticks=40)
fig.show()

ferrarisDrivers = bigDF[(bigDF['constructorName'] == 'Ferrari') & (bigDF['year'] >= 1990)]
ferrarisDrivers = ferrarisDrivers[['driverName', 'year']]
ferrarisDrivers = ferrarisDrivers.drop_duplicates(subset='driverName')
print(ferrarisDrivers)

bins = [1990, 2000, 2010, 2020]
labels = ['1990-1999', '2000-2009', '2010-2019']

ferrarisDrivers['year_group'] = pd.cut(ferrarisDrivers['year'], bins=bins, labels=labels, right=False)
ferrarisDrivers = ferrarisDrivers['year_group'].value_counts().reset_index()

fig = px.pie(ferrarisDrivers, names='index', values='year_group', hole=0.6,
             title='Nombre de pilotes chez Ferrari de 1990 à 2020', width=500)
fig.update_layout(annotations=[dict(text='Pilotes', x=0.5, y=0.5, font_size=30, showarrow=False)])
fig.show()
