import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.offline as py
import plotly.graph_objs as go


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# colors = {
#     'background': '#fff',
#     # 'text': '#7FDBFF'
#     'text': '#000'
# }


matches = pd.read_csv('matches.csv')
delivery = pd.read_csv('deliveries.csv')

# matches = pd.read_csv('../Dash/matches.csv')
# delivery = pd.read_csv('../Dash/deliveries.csv')
# matches = pd.read_csv('./Dash/matches.csv')
# delivery = pd.read_csv('./Dash/deliveries.csv')

# Dropping column since all values are NaN
matches.drop(['umpire3'], axis=1, inplace=True)
# Replacing the Team Names with their abbreviations
matches.replace(['Mumbai Indians', 'Kolkata Knight Riders', 'Royal Challengers Bangalore', 'Deccan Chargers', 'Chennai Super Kings',
                 'Rajasthan Royals', 'Delhi Daredevils', 'Gujarat Lions', 'Kings XI Punjab',
                 'Sunrisers Hyderabad', 'Rising Pune Supergiants', 'Kochi Tuskers Kerala', 'Pune Warriors', 'Rising Pune Supergiant'], ['MI', 'KKR', 'RCB', 'DC', 'CSK', 'RR', 'DD', 'GL', 'KXIP', 'SRH', 'RPS', 'KTK', 'PW', 'RPS'], inplace=True)

totalVanue = matches['city'].nunique()
totalMatchesPlayed = matches.shape[0]
totalUmpires = matches['umpire1'].nunique()
highestWinsTeam = (matches['winner'].value_counts()).idxmax()
highestWinsNum = matches['winner'].value_counts().max()

# piechart for toss dicision
tossDecision = px.pie(
    data_frame=matches,
    values=matches['toss_decision'].value_counts(),
    names=matches['toss_decision'].unique(),
    hole=0.6,
    title='Percentage of Toss Decision',
    hover_name=matches['toss_decision'].unique(),
    # hover_data={
    #     'label': False
    # }
    # color_discrete_sequence=px.colors.qualitative.Set3
)

tossDecisionByYear = px.histogram(
    data_frame=matches,
    x='season',
    color='toss_decision',
    barmode='group',
    title='Toss Decision By Year',
    labels={
      'season': 'Year of Match Played',
      'count': 'Toss Count',
      'toss_decision': 'Toss Decision'
    },
    # color_discrete_sequence=px.colors.qualitative.Vivid
)
toss = matches['toss_winner'].value_counts()
tossDecisionByTeam = px.bar(
    data_frame=toss,
    x=toss.index,
    y=toss.values,
    title='Toss Win By Teams',
    labels={
        'index': 'Teams',
        'y': 'No. of Toss Wins'
    },
    color=toss.index,
    # color_discrete_sequence=px.colors.qualitative.Pastel
    color_discrete_sequence=px.colors.qualitative.Plotly
)


# Matches win out of total matches played
matches_played_byteams = pd.concat([matches['team1'], matches['team2']])
matches_played_byteams = matches_played_byteams.value_counts().reset_index()
matches_played_byteams.columns = ['Team', 'Total Matches']
matches_played_byteams['wins'] = matches['winner'].value_counts().reset_index()[
    'winner']
matches_played_byteams.set_index('Team', inplace=True)
# trace1 = go.Bar(
#     x=matches_played_byteams.index,
#     y=matches_played_byteams['Total Matches'],
#     name='Matches Lost'
# )
# trace2 = go.Bar(
#     x=matches_played_byteams.index,
#     y=matches_played_byteams['wins'],
#     name='Matches Won'
# )
# data = [trace1, trace2]
# data[0].y = data[0].y - data[1].y
# layout = go.Layout(
#     barmode='stack'
# )
# totalMatchesVsWin = go.Figure(data=data, layout=layout)
matches_played_byteams['lost'] = matches_played_byteams['Total Matches'] - \
    matches_played_byteams['wins']
totalMatchesVsWin = px.bar(
    data_frame=matches_played_byteams,
    x=matches_played_byteams.index,
    y=['wins', 'lost'],
    barmode='stack',
    hover_name=matches_played_byteams.index,
    hover_data={
        'variable': False,
        'Total Matches': True
    },
    labels={
        'Team': 'Team',
        'value': 'No. of Matches',
        'variable': 'Match Result'
    },
    title='Total Matches vs Wins'
)

# Is Toss winner also the Match winner?
win = matches[matches['toss_winner'] == matches['winner']]
slices = [len(win), (577-len(win))]
isTossAlsoMatch = px.pie(
    data_frame=slices,
    values=slices,
    names=['Yes', 'No'],
    title='Is Toss Winner also the Match Winenr?'
)


# All About Runs
# total runs in season
batsmen = matches[['id', 'season']].merge(
    delivery, left_on='id', right_on='match_id', how='left').drop('id', axis=1)
season = batsmen.groupby(['season'])['total_runs'].sum().reset_index()
runsBySeason = px.line(
    data_frame=season,
    x='season',
    y='total_runs',
    labels={
      'season': 'Season',
      'total_runs': 'Total Runs scored'
    },
    title='Total Runs Scored in each Season'
)

# average runs in match per season
avgruns_each_season = matches.groupby(['season']).count().id.reset_index()
avgruns_each_season.rename(columns={'id': 'matches'}, inplace=1)
avgruns_each_season['total_runs'] = season['total_runs']
avgruns_each_season['average_runs_per_match'] = avgruns_each_season['total_runs'] / \
    avgruns_each_season['matches']
dff = avgruns_each_season.set_index('season')['average_runs_per_match']
averageRunByMatch = px.line(
    data_frame=dff,
    x=dff.index,
    y=dff.values,
    title='Average runs per match across Seasons',
    labels={
        'season': 'Season',
        'y': 'Average Runs'
    }
)

# runs per over by team across seasons
runsPerOver = delivery.pivot_table(
    index=['over'], columns='batting_team', values='total_runs', aggfunc=sum)
runsPerOver = runsPerOver.reset_index()
runsPerOverByTeam = px.line(
    data_frame=runsPerOver,
    x='over',
    y=runsPerOver.columns[1:],
    title='Runs per Over by Teams across Seasons',
    labels={
      'value': 'Total Runs'
    }
)

# Score Distribution for teams by innings
dff = delivery.groupby(['match_id', 'inning', 'batting_team'])[
    'total_runs'].sum().reset_index()
dff.drop('match_id', axis=1, inplace=True)
dff = dff.sort_values(by=['batting_team', 'total_runs'], ascending=True)
score1 = dff[dff['inning'] == 1]
score2 = dff[dff['inning'] == 2]

score1stInning = px.box(
    data_frame=score1,
    x='batting_team',
    y='total_runs',
    color='batting_team',
    title='Score Distributin fot Team in their 1st Innings',
    labels={
        'batting_team': 'Teams',
        'total_runs': 'Runs'
    },
    color_discrete_sequence=px.colors.qualitative.Plotly
)

score2ndInning = px.box(
    data_frame=score2,
    x='batting_team',
    y='total_runs',
    color='batting_team',
    title='Score Distributin fot Team in their 2nd Innings',
    labels={
        'batting_team': 'Teams',
        'total_runs': 'Runs'
    },
    color_discrete_sequence=px.colors.qualitative.Plotly
)


# Bowlers
bowlers = delivery.groupby('bowler').sum().reset_index()
bowl = delivery['bowler'].value_counts().reset_index()
bowlers = bowlers.merge(bowl, left_on='bowler', right_on='index', how='left')
bowlers = bowlers[['bowler_x', 'total_runs', 'bowler_y']]
bowlers.rename({'bowler_x': 'bowler', 'total_runs': 'runs_given',
               'bowler_y': 'balls'}, axis=1, inplace=True)
bowlers['overs'] = (bowlers['balls']//6)
dismissal_kinds = ["bowled", "caught", "lbw",
                   "stumped", "caught and bowled", "hit wicket"]
ct = delivery[delivery["dismissal_kind"].isin(dismissal_kinds)]
ct = ct['bowler'].value_counts().reset_index()
bowlers = bowlers.merge(ct, left_on='bowler',
                        right_on='index', how='left').dropna()
bowlers = bowlers[['bowler_x', 'runs_given', 'overs', 'bowler_y']]
bowlers.rename({'bowler_x': 'bowler', 'bowler_y': 'wickets'},
               axis=1, inplace=True)
bowlers['economy'] = (bowlers['runs_given']/bowlers['overs'])

bowlersScatter = px.scatter(
    data_frame=bowlers,
    x='overs',
    y='runs_given',
    color='bowler',
    size='wickets',
    title='Bowling Performence',
    labels={
        'overs': 'Overs',
        'runs_given': 'Given Runs',
        'bowler': 'Bowlers'
    },
    # color_discrete_sequence=px.colors.qualitative.Plotly
)

# Batsman
balls = delivery.groupby(['batsman'])['ball'].count().reset_index()
runs = delivery.groupby(['batsman'])['batsman_runs'].sum().reset_index()
balls = balls.merge(runs, left_on='batsman', right_on='batsman', how='outer')
balls.rename({'ball': 'ball_x', 'batsman_runs': 'ball_y'},
             axis=1, inplace=True)
sixes = delivery.groupby('batsman')['batsman_runs'].agg(
    lambda x: (x == 4).sum()).reset_index()
fours = delivery.groupby(['batsman'])['batsman_runs'].agg(
    lambda x: (x == 6).sum()).reset_index()
balls['strike_rate'] = balls['ball_y']/balls['ball_x']*100
balls = balls.merge(sixes, left_on='batsman', right_on='batsman', how='outer')
balls = balls.merge(fours, left_on='batsman', right_on='batsman', how='outer')
compare = delivery.groupby(["match_id", "batsman", "batting_team"])[
    "batsman_runs"].sum().reset_index()
compare = compare.groupby(['batsman', 'batting_team'])[
    'batsman_runs'].max().reset_index()
balls = balls.merge(compare, left_on='batsman',
                    right_on='batsman', how='outer')
balls.rename({'ball_x': 'balls', 'ball_y': 'runs', 'batsman_runs_x': "6's", 'batsman_runs_y': "4's",
             'batting_team': 'Team', 'batsman_runs': 'Highest_score'}, axis=1, inplace=True)

batsmanScatter = px.scatter(
    data_frame=balls,
    x='balls',
    y='runs',
    size='strike_rate',
    color='batsman',
    title='Batting Performence',
    labels={
        'balls': 'Balls Played',
        'runs': 'Runs'
    },
    # color_discrete_sequence=px.colors.qualitative.Plotly
)


# # styling figure
# figures = [isTossAlsoMatch, tossDecision, tossDecisionByYear,
#            tossDecisionByTeam, totalMatchesVsWin, runsBySeason,
#            averageRunByMatch, runsPerOverByTeam, score1stInning,
#            score2ndInning, bowlersScatter, batsmanScatter]
# for item in figures:
#     item.update_layout(
#         plot_bgcolor=colors['background'],
#         paper_bgcolor=colors['background'],
#         font_color=colors['text']
#     )


app.layout = html.Div([
    html.H1(
        'IPL Dashboard',
        style={
            'textAlign': 'center'
        }
    ),

    # Basic Data Analysis
    html.Div([
        html.P('Total vanues played at: {}'.format(totalVanue)),
        html.P('Total Matches Played: {}'.format(totalMatchesPlayed)),
        html.P('Total Umpires: {}'.format(totalUmpires)),
        html.P('Highes Number of Match Wins: {0}({1} wins)'.format(
            highestWinsTeam, highestWinsNum))
    ], id='basic-data-analysis', style={'columnCount': '2', 'textAlign': 'center'}),

    # Plotting Graphs about toss
    html.H3(
        'Making Toss Decisions',
        style={'textAlign': 'center'}
    ),
    html.Div([
        dcc.Graph(
            id='toss-decision',
            figure=tossDecision
        ),

        dcc.Graph(
            id='toss-decision-by-year',
            figure=tossDecisionByYear
        ),

        dcc.Graph(
            id='toss-decision-by-team',
            figure=tossDecisionByTeam
        )
    ], id='plotting-graph', style={'columnCount': '3'}),

    # Winning a Match
    html.H3(
        'Winnig a Match',
        style={'textAlign': 'center'}
    ),
    html.Div([
        dcc.Graph(
            id='total-matches-vs-win',
            figure=totalMatchesVsWin
        ),

        dcc.Graph(
            id='is-toss-also-match',
            figure=isTossAlsoMatch
        )
    ], id='winning-match', style={'columnCount': '2'}),

    # All about Runs
    html.H3(
        'All about Runs',
        style={'textAlign': 'center'}
    ),
    html.Div([
        dcc.Graph(
            id='runs-by-season',
            figure=runsBySeason,
        ),

        dcc.Graph(
            id='average-runs-per-match',
            figure=averageRunByMatch,
        ),

        dcc.Graph(
            id='runs-per-over',
            figure=runsPerOverByTeam
        )
    ], id='all-about-runs', style={'columnCount': '3'}),

    html.H3(
        'Team Performence',
        style={'textAlign': 'center'}
    ),
    html.Div([
        dcc.Graph(
            id='score-1st-inning',
            figure=score1stInning
        ),
        dcc.Graph(
            id='score-2nd-inning',
            figure=score2ndInning
        )

    ], id='about-runs-again', style={'columnCount': '2'}),

    html.H3(
        'Player\'s Performence',
        style={'textAlign': 'center'}
    ),
    html.Div([
        dcc.Graph(
            id='bowlers-scatter',
            figure=bowlersScatter
        ),
        dcc.Graph(
            id='batsman-scatter',
            figure=batsmanScatter
        )
    ], id='performence', style={'columnCount': '2'})

],
    #     style={
    #     'backgroundColor': colors['background'],
    #     'color': colors['text']
    # }
)

if __name__ == '__main__':
    app.run_server(debug=True)
