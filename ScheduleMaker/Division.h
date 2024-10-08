#pragma once

#include "Team.h"

#include <vector>

struct Division {
    std::string name = "";
    std::vector<Team> teams;
};