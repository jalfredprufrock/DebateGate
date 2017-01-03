from flask import Flask, render_template, request, url_for
from flask_mysqldb import MySQL
import datetime

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'electionproject.cgfgn1d8xb6e.us-east-1.rds.amazonaws.com'
app.config['MYSQL_USER'] = 'gchronis01'
app.config['MYSQL_PASSWORD'] = '12345678'
app.config['MYSQL_DB'] = 'mydb'
mysql = MySQL(app)

def execute_query(query):
	cur = mysql.connection.cursor()
	cur.execute(query)
	rv = cur.fetchall()
	data = [row for row in rv]
	return data


@app.route("/", methods=['GET', 'POST'])
def index():
	if request.method == 'GET':
		return render_template('candidate.html', method='get')
	if request.method == 'POST':
		candidate_name = request.form['candidate_name']
		performance = request.form['performance']
		first_debate = request.form['first_debate']
		second_debate = request.form['second_debate']

		if int(first_debate) > int(second_debate):
			first_debate, second_debate = second_debate, first_debate

		if performance == 'increase':
			query = '''Select p1.State, p2.%s-p1.%s as Increase from Polls p1, Polls p2 where (p1.State = p2.State) AND (p1.DebateNumber = %s AND p2.DebateNumber = %s) AND (p2.%s-p1.%s > 0) order by Increase DESC''' % (candidate_name, candidate_name, first_debate, second_debate, candidate_name, candidate_name)
		else:
			query = '''Select p1.State, p2.%s-p1.%s as Decrease from Polls p1, Polls p2 where (p1.State = p2.State) AND (p1.DebateNumber = %s AND p2.DebateNumber = %s) AND (p2.%s-p1.%s < 0) order by Decrease ASC''' % (candidate_name, candidate_name, first_debate, second_debate, candidate_name, candidate_name)

		data = execute_query(query)
		return render_template('candidate.html', data=data, method='post', performance=performance.upper())

@app.route("/history", methods=['GET', 'POST'])
def history():
	if request.method == 'GET':
		return render_template('history.html', method='get')
	if request.method == 'POST':
		party = request.form['party']
		position = request.form['position']
		outcome = request.form['outcome']

		if (party == 'dem' and position == 'ahead' and outcome == 'won') or (party == 'rep' and position == 'behind' and outcome == 'lost'):
			query = '''select h1.year, h1.democrat, h1.republican, h1.democrat_numbers, h1.republican_numbers, h2.democrat_numbers, h2.republican_numbers from historical_polls h1, (Select * from historical_polls where debate_number = 3) h2 where h1.debate_number = 0 and h1.democrat_numbers > h1.republican_numbers and h1.dem_won = "true" and h1.year = h2.year'''
		elif (party == 'dem' and position == 'ahead' and outcome == 'lost') or (party == 'rep' and position == 'behind' and outcome == 'won'):
			query = '''select h1.year, h1.democrat, h1.republican, h1.democrat_numbers, h1.republican_numbers, h2.democrat_numbers, h2.republican_numbers from historical_polls h1, (Select * from historical_polls where debate_number = 3) h2 where h1.debate_number = 0 and h1.democrat_numbers > h1.republican_numbers and h1.dem_won = "false" and h1.year = h2.year'''
		elif (party == 'dem' and position == 'behind' and outcome == 'won') or (party == 'rep' and position == 'ahead' and outcome == 'lost'):
			query = '''select h1.year, h1.democrat, h1.republican, h1.democrat_numbers, h1.republican_numbers, h2.democrat_numbers, h2.republican_numbers from historical_polls h1, (Select * from historical_polls where debate_number = 3) h2 where h1.debate_number = 0 and h1.democrat_numbers < h1.republican_numbers and h1.dem_won = "true" and h1.year = h2.year'''
		elif (party == 'dem' and position == 'behind' and outcome == 'lost') or (party == 'rep' and position == 'ahead' and outcome == 'won'):
			query = '''select h1.year, h1.democrat, h1.republican, h1.democrat_numbers, h1.republican_numbers, h2.democrat_numbers, h2.republican_numbers from historical_polls h1, (Select * from historical_polls where debate_number = 3) h2 where h1.debate_number = 0 and h1.democrat_numbers < h1.republican_numbers and h1.dem_won = "false" and h1.year = h2.year'''

		data = execute_query(query)
		return render_template('history.html', data=data, method='post')

@app.route("/state", methods=['GET', 'POST'])
def state():
	if request.method == 'GET':
		return render_template('state.html', method='get')
	if request.method == 'POST':
		state = request.form['state']
		data = execute_query('''Select * from Polls where State = "%s"''' % (state))
		return render_template('state.html', data=data, method='post')

@app.route("/electoral", methods=['GET', 'POST'])
def electoral():
	if request.method == 'GET':
		return render_template('electoral.html', method='get')
	if request.method == 'POST':
		lower_bound = request.form['lower_bound']
		upper_bound = request.form['upper_bound']
		first_debate = request.form['first_debate']
		second_debate = request.form['second_debate']

		if lower_bound == '':
			lower_bound = "3"

		if upper_bound == '':
			upper_bound = "55"

		if int(first_debate) > int(second_debate):
			first_debate, second_debate = second_debate, first_debate

		data = execute_query('''Select p1.State, p2.Clinton-p1.Clinton, p2.Trump - p1.Trump from Polls p1, Polls p2, (select * from states where electoral_votes >= %s and electoral_votes <= %s) s1 where (p1.State = p2.State) AND (p1.State = s1.State) AND (p1.DebateNumber = %s AND p2.DebateNumber = %s)''' % (lower_bound, upper_bound, first_debate, second_debate))
		return render_template('electoral.html', data=data, method='post')

@app.route("/demographics", methods=['GET', 'POST'])
def demographics():
	if request.method == 'GET':
		return render_template('demographics.html', method='get')
	if request.method == 'POST':
		demographics_type = request.form['demographics_type']
		first_debate = request.form['first_debate']
		second_debate = request.form['second_debate']

		if int(first_debate) > int(second_debate):
			first_debate, second_debate = second_debate, first_debate

		data = execute_query('''Select d1.demographic, d2.clinton_percent-d1.clinton_percent, d2.trump_percent- d1.trump_percent from Demographics d1, Demographics d2 where (d1.demographic = d2.demographic) AND (d1.debate_number = %s AND d2.debate_number = %s) AND d1.type = "%s"''' % (first_debate, second_debate, demographics_type))
		return render_template('demographics.html', data=data, method='post')

@app.route("/dates", methods=['GET', 'POST'])
def dates():
	if request.method == 'GET':
		return render_template('dates.html', method='get')
	if request.method == 'POST':
		month = request.form['month']
		day = request.form['day']
		event = request.form['event']

		try:
			original_date = datetime.date(2016, int(month), int(day))
		except:
			original_date = datetime.date(2016, int(month), int(day)-1)
		
		day_before = str(original_date - datetime.timedelta(days=1))
		week_before = str(original_date - datetime.timedelta(days=7))
		day_after = str(original_date + datetime.timedelta(days=1))
		week_after = str(original_date + datetime.timedelta(days=7))
		original_date = str(original_date)

		if event == '':
			event = original_date

		data = execute_query('''SELECT avg(dt1.clinton) as b4clinton, avg (dt1.trump) as b4trump, afterclinton, aftertrump FROM ( select clinton, trump from events where day>="%s" and day<="%s" ) as dt1, (SELECT  avg(dt2.clinton) as afterclinton, avg (dt2.trump) as aftertrump FROM ( select clinton, trump from events where day>="%s" and day<="%s" ) as dt2) as this_table''' % (week_before, day_before, day_after, week_after))
		return render_template('dates.html', data=data, event=event, method='post')


if __name__ == "__main__":
	app.debug = True
	app.run()