import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Web Scraping

df = pd.read_html("https://covidlive.com.au/report/daily-cases/vic")[1]
df.columns = ['Date', 'Total Cases', 'VAR', 'Net Cases']
del df['VAR']
df.head()

#Data Cleaning

data = []
for date, cum, net_cases, in zip(df['Date'], df['Total Cases'], df['Net Cases']):
    # format the date as YYYY-MM-DD
    date = datetime.strptime(date + ' 2020', "%d %b %Y")
    # add the row to the array
    data.append([date, cum, net_cases])

# Data Export

# create a new data frame from our clean data
cleaned = pd.DataFrame(data)
# update column names
cleaned.columns = ['date', 'total_cases', 'net_cases']
# set no change in cases to zero
cleaned['net_cases'] = cleaned['net_cases'].replace('-', 0)
# convert nets to float
cleaned['net_cases'] = cleaned['net_cases'].astype(int)

# lockdown dates
lockdowns = [
    # stage name, start date, colour, show hatching
    ['Stage 1', np.datetime64('2020-03-23', 'h'), '#bad80a', False],
    ['Stage 2', np.datetime64('2020-03-26', 'h'), '#009e49', False],
    ['Stage 3', np.datetime64('2020-03-31', 'h'), '#00b294', False],
    ['Stage 2 (again)', np.datetime64('2020-06-01', 'h'), '#00bcf2', False],
    ['Stage 3 (postcodes)', np.datetime64('2020-07-02', 'h'), '#00188f', True],
    ['Stage 3 (again)', np.datetime64('2020-07-08', 'h'), '#68217a', False],
    ['Masks', np.datetime64('2020-07-23', 'h'), '#ec008c', False],
    ['Stage 4', np.datetime64('2020-08-02', 'h'), '#e81123', False],
    ['Stage 4 Ends', np.datetime64('2020-09-13', 'h'), '#ff8c00', True],
    ['First Step', np.datetime64('2020-09-14', 'h'), '#ff8c00', False],
    ['Second Step', np.datetime64('2020-09-28', 'h'), '#ff8c00', False],
    ['Third Step', np.datetime64('2020-10-19', 'h'), '#ff8c00', False],
    ['Fourth Step', np.datetime64('2020-11-09', 'h'), '#ff8c00', False],
    ['COVID Normal', np.datetime64('2020-11-30', 'h'), '#ff8c00', False],
]


# https://hihayk.github.io/scale/
colors = [
    '#0A8251',
    '#1C8B89',
    '#2D6F94',
    '#3F579D',
    '#5C51A6',
    '#8A62B0',
    '#B274B9',
    '#C286B1',
    '#CB97A8',
    '#D4ABA9',
    '#DDCABB',
    '#E6E1CD',
    '#EBEFDE',
    '#F3F8F0'
]

colors = [x for x in reversed(colors)]
# set the alpha for the colors
ALP = 0.75

def calculate_fortnight_average(row):
    # get the date of the current row we are looking at 
    date = row['date']
    
    # calculate the range of dates, e.g. take 14 days from the row's date
    two_weeks_ago = date - timedelta(days=14)
    filt = (cleaned['date'] > two_weeks_ago) & (cleaned['date'] < date)
    
    # filter the overall data set for these values
    days = cleaned[filt]
    
    # get the net cases for every day in this range
    net_cases_fortnight = [x for x in days['net_cases'].values]
    
    return sum(net_cases_fortnight)/14

# for every cell in the data, calculate the 14 day average
cleaned['fortnight_average'] = cleaned.apply(lambda x: calculate_fortnight_average(x), axis=1)

# export the cleaned data
try:
	cleaned.to_csv('exported_covid_data.csv', index=False)
except:
	pass

def covid_plot(show_plot=False):
	fig, axes = plt.subplots(2, figsize=(18, 12))

	MAX_CASES = cleaned['net_cases'].max()
	DAYS = (cleaned['date'].max()-cleaned['date'].min()).days

	chart = sns.lineplot(x='date', y='net_cases', data=cleaned, ax=axes[0], linewidth=1.5)

	for i in range(0, len(lockdowns)-1):
	    axes[0].fill_betweenx(
	        y=[0, MAX_CASES+5],
	        x1=[lockdowns[i][1], lockdowns[i][1]],
	        x2=[lockdowns[i+1][1], lockdowns[i+1][1]],
	        alpha=ALP,
	        label=lockdowns[i][0],
	        color=colors[i],
	        hatch='///' if lockdowns[i][3] else ''
	    )
	    
	# add a line for today
	today_str = f'Today ({datetime.now().strftime("%b %d")})'
	axes[0].axvline(datetime.now(), 0, MAX_CASES, label=today_str, color='red', alpha=0.75)
	    
	fig.legend(title='Lockdown Type', ncol=2, loc='upper right')

	# add titles
	axes[0].set_title(f'Daily Net Cases')
	axes[0].set_ylabel("New Cases")
	axes[0].set_xlabel("Date")

	# 14 day average plot, axis 1

	chart = sns.lineplot(x='date', y='fortnight_average', data=cleaned, ax=axes[1], linewidth=1.5)

	# set the y ticks to increment by 50
	MAX_AVG = int(cleaned['fortnight_average'].max())
	ticks = [str(x) for x in range(0, MAX_AVG, 50)]
	chart.set_yticks(range(0, MAX_AVG, 50))
	chart.set_yticklabels(ticks)

	for i in range(0, len(lockdowns)-1):
	    axes[1].fill_betweenx(
	        y=[0, MAX_AVG+5],
	        x1=[lockdowns[i][1], lockdowns[i][1]],
	        x2=[lockdowns[i+1][1], lockdowns[i+1][1]],
	        alpha=ALP,
	        label=lockdowns[i][0],
	        color=colors[i],
	        hatch='///' if lockdowns[i][3] else '',
	    )
	    
	# add a vertical line for today
	axes[1].axvline(datetime.now(), 0, MAX_AVG, label=today_str, color='red', alpha=0.75)
	    
	# add titles
	axes[1].set_title(f'Rolling 14 day average')
	axes[1].set_ylabel("14 day average")
	axes[1].set_xlabel("Date")

	today = datetime.now().strftime("%d/%m/%Y")
	plt.suptitle(f"Victoria's COVID-19 over {DAYS} days\nLast updated {today}")
	fig.savefig('victorian_covid_plot.png', bbox_inches="tight")

	if show_plot:
		plt.show()

covid_plot()
