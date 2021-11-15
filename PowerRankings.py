from espn_api.basketball import League
import pandas as pd
import numpy as np

league = League(league_id=1946371300, year=2022)
current_week = 4

# url = "https://fantasy.espn.com/apis/v3/games/fba/seasons/" + \
#     str(year) + "/segments/0/leagues/" + str(league_id)

# NOTE: Does not work now
def generatePointsRankings():
    response = requests.get(url, params={"view": "mMatchup"})
    print(response.status_code)
    data = response.json()
    current_week = 0
    max_strength = 0
    min_strength = 0
    max_t_score = 0
    num_of_weeks = 4.0 # number of weeks to look back at for rankings

    # points difference, wins, calculated strength, and t-score in last 4 matchups
    # ORDER OF TEAMS MATTERS!!!!! it is same as order in "league members" tab
    team_strength = [
        ["Tyler", 0, 0, 0, 0], ["Henry", 0, 0, 0, 0], ["Ib", 0, 0, 0, 0],
        ["Zack", 0, 0, 0, 0], ["Holden", 0, 0, 0, 0], ["Lucas", 0, 0, 0, 0],
        ["Connor", 0, 0, 0, 0], ["Daniel", 0, 0, 0, 0], ["Jimmy", 0, 0, 0, 0],
        ["Torrien", 0, 0, 0, 0], ["Nick", 0, 0, 0, 0], ["Linus", 0, 0, 0, 0]
    ]

    # t score is the adjusted score for strength of schedule/quality of wins
    team_t_score = team_strength

    # create dataframe of all matchups so far
    matchup_df = [[
        game['matchupPeriodId'],
        game['home']['teamId'], game['home']['totalPoints'],
        game['away']['teamId'], game['away']['totalPoints']
    ] for game in data['schedule']]

    # find current week. this only works on monday before any games have been played. don't know where
    # in ESPN's api to find wins/losses which would be better method
    for matchup in matchup_df:
        if int(matchup[2]) != 0: # if matchup has happened
            current_week = int(matchup[0])

    # calculate total point differential over last x weeks
    for matchup in matchup_df:
        if matchup[0] <= current_week and matchup[0] > current_week - num_of_weeks:
            print(matchup)
            team_strength[matchup[1] - 1][1] += matchup[2] - matchup[4]
            if matchup[2] > matchup[4]:
                team_strength[matchup[1] - 1][2] += 1
            team_strength[matchup[3] - 1][1] += matchup[4] - matchup[2]
            if matchup[4] > matchup[2]:
                team_strength[matchup[3] - 1][2] += 1

    # round point differentials and find max/min strength
    for i in range(len(team_strength)):
        team_strength[i][1] = round(team_strength[i][1], 1)
        if team_strength[i][1] > max_strength:
            max_strength = team_strength[i][1]
        elif team_strength[i][1] < min_strength:
            min_strength = team_strength[i][1]

    # find team strength
    for i in range(len(team_strength)):
        wins = team_strength[i][2]
        # team strength is point differential relative to highest (or lowest) point
        # differential, which is then adjusted for number of recent wins. that way
        # if you suck but have 2 wins, you get strength boost, or if you have high
        # point differential but only won 2 times, you get docked
        if team_strength[i][1] > 0:
            team_strength[i][3] = round((team_strength[i][1] / max_strength) *
                                        (wins / num_of_weeks), 3)
        elif team_strength[i][1] < 0:
            try:
                team_strength[i][3] = round((team_strength[i][1] / -min_strength) *
                                            ((num_of_weeks - wins) / num_of_weeks),
                                            3)
            except ZeroDivisionError:
                team_strength[i][3] = round(team_strength[i][1] / -min_strength)

    # calculate t score based on quality of wins
    for matchup in matchup_df:
        if matchup[0] > current_week - num_of_weeks:
            if matchup[2] > matchup[4]:
                # if winning team was worse team
                if team_strength[matchup[1] - 1][3] < team_strength[matchup[3] -
                1][3]:
                    # add better team's strength to t-score
                    team_strength[matchup[1] - 1][4] += (
                        team_strength[matchup[3] - 1][3] + 1.0)
                    # subtract better team t-score - worse team t-score
                    team_strength[matchup[3] - 1][4] -= (
                        (team_strength[matchup[3] - 1][3] + 1.0) -
                        (team_strength[matchup[1] - 1][3] + 1.0)
                    )
                else:
                    # if winning team was better team
                    team_strength[matchup[1] - 1][4] += (
                        team_strength[matchup[3] - 1][3] + 1.0)
                    team_strength[matchup[3] - 1][4] -= (
                        2.0 - (team_strength[matchup[1] - 1][3] + 1.0)
                    )
            elif matchup[4] > matchup[2]:
                # if winning team was worse team
                if team_strength[matchup[1] - 1][3] > team_strength[matchup[3] -
                1][3]:
                    # add better team's strength to t-score
                    team_strength[matchup[3] - 1][4] += (
                        team_strength[matchup[1] - 1][3] + 1.0)
                    # subtract better team t-score - worse team t-score
                    team_strength[matchup[1] - 1][4] -= (
                        (team_strength[matchup[1] - 1][3] + 1.0) -
                        (team_strength[matchup[3] - 1][3] + 1.0)
                    )
                else:
                    # if winning team was better team
                    team_strength[matchup[3] - 1][4] += (
                        (team_strength[matchup[1] - 1][3] + 1.0)
                    )
                    team_strength[matchup[1] - 1][4] -= (
                        2.0 - (team_strength[matchup[3] - 1][3] + 1.0)
                    )

    print("Max Strength: " + str(max_strength) + ", Min Strength: " +
        str(min_strength))

    print("Team Strength: ")
    for team in team_strength:
        print(team[0] + ": " + str(team[1]) + " +/-, " + str(team[2]) + " wins, " +
            str(team[3]) + " overall strength, " + str(team[4]) + " T-Score.")

    # sort by T-Score
    for i in range(len(team_strength)):
        for j in range(len(team_strength)):
            if team_strength[j][4] < team_strength[i][4]:
                temp_team = team_strength[i]
                team_strength[i] = team_strength[j]
                team_strength[j] = temp_team

    print("")

    # final rankings
    print(" Week " + str(int(current_week) + 1) + " Power Rankings: ")
    for i in range(len(team_strength)):
        print(" " + str(i + 1) + ". " + team_strength[i][0] + ": " +
            str(round(team_strength[i][4], 3)))

    print("")

class LeagueTeam:
    def __init__(self):
        self.name = ""
        self.categories = {"PTS" : 0, "REB" : 0, "AST" : 0, "STL" : 0, "BLK" : 0, "3PTM" : 0, "FGM" : 0, "FGA" : 0, "FG%" : 0, "FTM" : 0, "FTA" : 0, "FT%" : 0, "TO" : 0}
        self.rosterSize = 0

def generateCategoriesRankings():
    leagueTeams = {}
    for team in league.teams:
        leagueTeams[team.team_name] = LeagueTeam()
        leagueTeams[team.team_name].name = team.team_name
        for player in team.roster:
            try:
                for cat in leagueTeams[team.team_name].categories:
                    leagueTeams[team.team_name].categories[cat] += player.stats['last_30_2022']['total'][cat]
                    leagueTeams[team.team_name].rosterSize += 1
            except KeyError:
                True

    data = []
    for team in leagueTeams:
        t = leagueTeams[team]
        t.categories["FG%"] = round(leagueTeams[team].categories["FGM"] / leagueTeams[team].categories["FGA"], 4) * 100
        t.categories["FT%"] = round(leagueTeams[team].categories["FTM"] / leagueTeams[team].categories["FTA"], 4) * 100
        data.append([t.name, t.categories["PTS"], t.categories["REB"], t.categories["AST"], t.categories["STL"], t.categories["BLK"], t.categories["3PTM"], t.categories["FG%"], t.categories["FT%"], t.categories["TO"]])

    df = pd.DataFrame(data, columns=["Team Name", "PTS", "REB", "AST", "STL", "BLK", "3PTM", "FG%", "FT%", "TO"])
    rankedData = []
    for team in leagueTeams:
        teamRanks = [team]
        totalRank = 0
        for column in df:
            if(column == "Team Name"):
                continue
            df = df.sort_values(by=[column], ascending=False)
            rank = 1
            for i in range(12):
                if(df.iloc[i]["Team Name"] == leagueTeams[team].name):
                    teamRanks.append(rank)
                    totalRank += rank
                    continue
                rank += 1
        teamRanks.append(totalRank)
        rankedData.append(teamRanks)

    rankedDf = pd.DataFrame(rankedData)
    rankedDf.columns = ["Team Name", "PTS", "REB", "AST", "STL", "BLK", "3PTM", "FG%", "FT%", "TO", "Final Rank"]
    rankedDf = rankedDf.sort_values(by=["Final Rank"], ascending=True)
    rankedDf.index = np.arange(1, len(df) + 1)
    
    print("\nWeek " + str(current_week) + " Power Rankings\n")
    print(rankedDf)

generateCategoriesRankings()