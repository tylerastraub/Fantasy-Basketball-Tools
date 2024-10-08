#pragma once

#include "Division.h"

#include <vector>
#include <unordered_map>
#include <list>
#include <random>
#include <algorithm>
#include <chrono>
#include <iostream>

using Matchup = std::pair<Team, Team>;
using Schedule = std::unordered_map<int, std::vector<Matchup>>;

class Scheduler {
public:
    Scheduler() = default;
    ~Scheduler() = default;

    Schedule create() {
        _schedule.clear();
        unsigned seed = std::chrono::system_clock::now().time_since_epoch().count();
        std::default_random_engine rng(seed);

        // First create in-division games because that's easy
        for(auto division : _divisions) {
            // calculate matchups using round robin algorithm
            std::vector<std::vector<Matchup>> allMatchups;
            std::shuffle(division.teams.begin(), division.teams.end(), rng);
            auto teams = division.teams;
            do {
                std::vector<Matchup> weekMatchups;
                weekMatchups.push_back(std::make_pair(teams[0], teams[1]));
                weekMatchups.push_back(std::make_pair(teams[2], teams[3]));
                allMatchups.push_back(weekMatchups);
                std::vector<Team> temp = {
                    teams[0], teams[3], teams[1], teams[2]
                };
                teams = temp;
            } while(division.teams[1].name != teams[1].name);

            // make it so each matchup happens 3 times
            auto temp = allMatchups;
            for(int i = 0; i < 2; ++i) {
                allMatchups.insert(allMatchups.end(), temp.begin(), temp.end());
            }
            // then add to schedule
            for(int i = 0; i < allMatchups.size(); ++i) {
                auto week = allMatchups[i];
                _schedule[i * 2 + 1].insert(_schedule[i * 2 + 1].end(), week.begin(), week.end());
            }
        }

        // Then create intra-divisional matchups
        std::vector<std::vector<Matchup>> allMatchups;
        std::vector<Team> teams;
        for(int i = 0; i < 4; ++i) {
            for(auto division : _divisions) {
                teams.push_back(division.teams[i]);
            }
        }

        // 8 out-of-division matchups
        for(int i = 0; i < 8; ++i) {
            std::vector<Matchup> weeklyMatchups;
            std::list<Team> pool;
            std::copy(teams.begin(), teams.end(), std::back_inserter(pool));

            while(pool.size() > 0) {
                Team team1 = *pool.begin();
                Team team2;
                auto it = pool.begin();
                int counter = 0;
                for(; it->division == team1.division; ++it) {
                    ++counter;
                    if(counter > 500) {
                        std::cout << "ERROR LOOPING!!!" << std::endl;
                        break;
                    }
                }
                team2 = *it;
                weeklyMatchups.push_back(std::make_pair(team1, team2));
                pool.erase(it);
                pool.pop_front();
            }

            allMatchups.push_back(weeklyMatchups);

            std::vector<Team> tempTeams = {teams[0], teams[teams.size() - 1]};
            for(int i = 1; i < teams.size() - 1; ++i) {
                tempTeams.push_back(teams[i]);
            }
            teams = tempTeams;
        }

        for(int i = 0; i < allMatchups.size(); ++i) {
            std::string str = "Week " + std::to_string(i + 1) + ": ";
            for(auto matchup : allMatchups[i]) {
                str.append(matchup.first.name + " - " + matchup.second.name + ", ");
            }
            str = str.substr(0, str.size() - 2);
            std::cout << str << std::endl;
        }

        return _schedule;
    }

    void addDivision(Division division) {
        _divisions.push_back(division);
    }

    void setTeams(std::vector<Division> divisions) {
        _divisions = divisions;
    }

private:
    const int NUM_OF_WEEKS = 17;
    const int DIVISION_TOURNAMENT_WEEKS[2] = {8, 10};

    std::vector<Division> _divisions = {};
    // week, matchup
    Schedule _schedule;

};