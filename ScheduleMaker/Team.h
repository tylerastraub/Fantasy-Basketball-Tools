#pragma once

#include <string>
#include <vector>

struct Team {
    std::string name = "";
    std::string division = "";
    std::vector<Team> matchups = {};
};