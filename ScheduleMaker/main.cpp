#include "Scheduler.h"

#include <iostream>

int main() {
    Scheduler scheduler;

    std::string divName = "Short Kings";
    Division shortKings = {
        divName,
        {{"Ib", divName}, {"Lucas", divName}, {"Torrien", divName}, {"Finn", divName}}
    };
    divName = "6ft on Tinder";
    Division sixFtOnTinder = {
        divName,
        {{"Daniel", divName}, {"Jimmy", divName}, {"Tyler", divName}, {"Milo", divName}}
    };
    divName = "PBR Tallboys";
    Division tallBoys = {
        divName,
        {{"Nick", divName}, {"Linus", divName}, {"Cade", divName}, {"Henry", divName}}
    };

    scheduler.addDivision(shortKings);
    scheduler.addDivision(sixFtOnTinder);
    scheduler.addDivision(tallBoys);

    auto schedule = scheduler.create();

    // for(int week = 1; week < 18; ++week) {
    //     std::string str = "Week " + std::to_string(week) + ": ";
    //     for(auto matchup : schedule[week]) {
    //         str.append(matchup.first.name + " vs. "  + matchup.second.name + ", ");
    //     }
    //     str = str.substr(0, str.size() - 2);
    //     std::cout << str << std::endl;
    // }

    return 0;
}