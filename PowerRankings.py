from espn_api.basketball import League
import pandas as pd
import numpy as np
from matplotlib import colormaps

league = League(league_id=1946371300, year=2025)
current_week = 3
num_of_weeks = 2

class LeagueTeam:
    def __init__(self):
        self.name = ""
        self.division = ""
        self.categories = {"PTS" : 0, "REB" : 0, "AST" : 0, "STL" : 0, "BLK" : 0, "3PM" : 0, "FGM" : 0, "FGA" : 0, "FG%" : 0, "FTM" : 0, "FTA" : 0, "FT%" : 0, "TO" : 0}
        self.wins = 0
        self.losses = 0
        self.ties = 0
        self.record = ""
        self.catsWon = 0
        self.catsLost = 0
        self.catsTied = 0

def generateCategoriesRankings():
    leagueTeams = {}
    # populate basic team info
    for team in league.teams:
        leagueTeams[team.team_name] = LeagueTeam()
        leagueTeams[team.team_name].name = team.team_name
        leagueTeams[team.team_name].division = team.division_name
        leagueTeams[team.team_name].wins = team.wins
        leagueTeams[team.team_name].losses = team.losses
        leagueTeams[team.team_name].ties = team.ties

    # get category totals over last n weeks
    for week in range(current_week - num_of_weeks, current_week):
        box_scores = league.box_scores(week, 0, True)
        for box_score in box_scores:
            if box_score.home_team.team_name in leagueTeams:
                home_team = leagueTeams[box_score.home_team.team_name]
                for cat in home_team.categories:
                    home_team.categories[cat] += box_score.home_stats[cat]["value"]
                    if box_score.home_stats[cat]["result"] == "WIN":
                        home_team.catsWon += 1
                    elif box_score.home_stats[cat]["result"] == "LOSS":
                        home_team.catsLost += 1
                    elif box_score.home_stats[cat]["result"] == "TIE":
                        home_team.catsTied += 1
            else:
                print("Error: key not found! " + box_score.home_team.team_name)
            if box_score.away_team.team_name in leagueTeams:
                away_team = leagueTeams[box_score.away_team.team_name]
                for cat in away_team.categories:
                    away_team.categories[cat] += box_score.away_stats[cat]["value"]
                    if box_score.away_stats[cat]["result"] == "WIN":
                        away_team.catsWon += 1
                    elif box_score.away_stats[cat]["result"] == "LOSS":
                        away_team.catsLost += 1
                    elif box_score.away_stats[cat]["result"] == "TIE":
                        away_team.catsTied += 1
            else:
                print("Error: key not found! " + box_score.away_team.team_name)

    # fix FG% and FT% to be more readable, then add data to dataframe
    data = []
    for team in leagueTeams:
        t = leagueTeams[team]
        t.categories["FG%"] = round(leagueTeams[team].categories["FGM"] / leagueTeams[team].categories["FGA"], 4) * 100
        t.categories["FT%"] = round(leagueTeams[team].categories["FTM"] / leagueTeams[team].categories["FTA"], 4) * 100
        if(t.ties > 0):
            record = "(" + str(t.wins) + "-" + str(t.losses) + "-" + str(t.ties) + ")"
        else:
            record = "(" + str(t.wins) + "-" + str(t.losses) + ")"
        leagueTeams[team].record = record
        data.append([t.name, t.division, record, t.categories["PTS"], t.categories["REB"], t.categories["AST"], t.categories["STL"], t.categories["BLK"], t.categories["3PM"], t.categories["FG%"], t.categories["FT%"], t.categories["TO"]])

    # dataframe sorting
    df = pd.DataFrame(data, columns=["Team Name", "Division", "Record", "PTS", "REB", "AST", "STL", "BLK", "3PM", "FG%", "FT%", "TO"])
    rankedData = []
    for team in leagueTeams:
        teamRanks = [team]
        teamRanks.append(leagueTeams[team].division)
        teamRanks.append(leagueTeams[team].record)
        totalRank = 0
        for column in df:
            if(column == "Team Name" or column == "Division" or column == "Record"):
                continue
            sortByAscending = False
            if(column == "TO"):
                sortByAscending = True
            df = df.sort_values(by=[column], ascending=sortByAscending)
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
    rankedDf.columns = ["Team Name", "Division", "Record", "PTS", "REB", "AST", "STL", "BLK", "3PM", "FG%", "FT%", "TO", "T-Score"]

    rankedDf = rankedDf.sort_values(by=["T-Score"], ascending=True)
    rankedDf.index = np.arange(1, len(df) + 1)
    print("\nWeek " + str(current_week) + " Power Rankings\n (pre rank mods)")
    print(rankedDf)
    print()

    # now that we have the "objective" team rankings, we can use wins/losses to adjust these ranks
    # below is old rank mods that adjusted based on strength of teams beat/lost to
    # startWeek = 1
    # if current_week - num_of_weeks > 1:
    #     startWeek = current_week - num_of_weeks

    # rankMods = {}
    # rankRange = rankedDf["T-Score"].max() - rankedDf["T-Score"].min()
    # for team in rankedDf.loc[:, "Team Name"]:
    #     rankMods[team] = 0
    # for i in range(num_of_weeks):
    #     matchups = league.scoreboard(startWeek + i)
    #     for matchup in matchups:
    #         if(matchup.winner == "HOME"):
    #             winner = matchup.home_team.team_name
    #             loser = matchup.away_team.team_name
    #         else:
    #             winner = matchup.away_team.team_name
    #             loser = matchup.home_team.team_name
    #         winnerRank = getTeamRank(winner, rankedDf)
    #         loserRank = getTeamRank(loser, rankedDf)
    #         rankDiff = winnerRank - loserRank
    #         if rankDiff + rankRange != 0:
    #             rankMods[winner] += (rankDiff + rankRange) / (rankRange * 2)
    #             rankMods[loser] -= (rankDiff + rankRange) / (rankRange * 2)
    
    # rankModifier = 6.0 # how much wins/losses should sway rank. if the worst team beats the best team, their rank improves by this much
    # for index, row in rankedDf.iterrows():
    #     oldRank = row["T-Score"]
    #     rankedDf.at[index, "T-Score"] -= rankMods[row["Team Name"]] * rankModifier
    #     print("Old rank for " + row["Team Name"] + ": " + str(oldRank) + ", new rank: " + str(rankedDf.at[index, "T-Score"]), ", rank modifier: " + str(rankMods[row["Team Name"]]))
    winModifier = 2
    catsModifier = 1 / num_of_weeks
    for index, row in rankedDf.iterrows():
        rankedDf.at[index, "T-Score"] -= leagueTeams[row["Team Name"]].wins * winModifier
        rankedDf.at[index, "T-Score"] -= round(leagueTeams[row["Team Name"]].catsWon * catsModifier)

    rankedDf = rankedDf.sort_values(by=["T-Score"], ascending=True)
    rankedDf.index = np.arange(1, len(df) + 1)
    # rankedDf["T-Score"] = rankedDf["T-Score"].astype(str).apply(Decimal)
    
    print("\nWeek " + str(current_week) + " Power Rankings\n")
    print(rankedDf[["Team Name", "Division", "Record", "T-Score"]])
    print()

    styles = [
        dict(selector='th', props=[('background', '#494949'),
                                   ('color', '#ffffff'),
                                   ('font-size', '14pt'),
                                   ('font-family', 'Calibri'),
                                   ('padding', '4px')]),
        dict(selector='tr:nth-child(even)', props=[('background', '#ece8d9')]),
        dict(selector='td', props=[('font-size', '12pt'),
                                   ('font-family', 'Calibri'),
                                   ('padding', '2px')]),
        dict(selector='caption', props=[('font-size', '18pt'),
                                        ('font-family', 'Calibri'),
                                        ('margin', '10px'),
                                        ('font-weight', 'bold')])
    ]
    output = open("power_rankings.html", "w")
    output.write(rankedDf.style
                         .set_caption("Week " + str(current_week) + " Power Rankings")
                         .set_table_styles(styles)
                         .background_gradient(axis=0, subset=["PTS", "REB", "AST", "STL", "BLK", "3PM", "FG%", "FT%", "TO"], cmap='RdYlGn_r')
                         .set_properties(subset=["T-Score"], **{'font-weight': 'bold'})
                         .to_html())
    output.close()

def getTeamRank(teamName, rankedData):
    for index, row in rankedData.iterrows():
        team = row["Team Name"]
        if team == teamName:
            return rankedData.loc[index]["T-Score"]

    return -1

generateCategoriesRankings()
