import numpy as np
import matplotlib.pyplot as plt
import random
from datetime import datetime
import os
import sys
import copy

U = 3

def checkScheduleConstraintsColumns(schedule, nrTeams):
    """Calculates the number of violations present in the columnFirst schedule

    Arguments:
        schedule ([int, int]) : Schedule 

        nrTeams (int) : The number of teams present in the schedule

    Returns:
        violations ([int]) : The number of violations present in the schedule, in the format [maxStreak, No-repeat, Double round-robin]
    """
    nrRounds = (2*nrTeams)-2
    violations = [0, 0, 0, 0, 0]
    maxStreak = np.zeros(nrTeams)

    for round in range(nrRounds):
        gamesNeeded = []
        for i in range(1, nrTeams+1):
            gamesNeeded.append(i)

        for team in range(nrTeams):
            # Check doubleRoundRobin (Each team appears once in each row)
            if abs(schedule[round, team]) in gamesNeeded:
                gamesNeeded.remove(abs(schedule[round, team]))
            
            # Check maxStreak
            if round > 0 and schedule[round-1, team] > 0 and schedule[round, team] > 0:
                maxStreak[team] += 1
            elif round > 0 and schedule[round-1, team] < 0 and schedule[round, team] < 0:
                maxStreak[team] += 1
            else:
                maxStreak[team] = 0

            if maxStreak[team] >= U:
                violations[0] += 1

            #Check if the opponent also has the current team as opponent (matches are paired) (Never happens but is used to check validity of schedules)
            # if team != abs(schedule[round, abs(schedule[round, team])-1])-1:
            #     violations[2] += 1
            # if schedule[round, team] < 0 and schedule[round, abs(schedule[round, team])-1] < 0:
            #     violations[2] += 1
            # if schedule[round, team] > 0 and schedule[round, abs(schedule[round, team])-1] > 0:
            #     violations[2] += 1

            # Check noRepeat
            if round > 0 and abs(schedule[round-1, team]) == abs(schedule[round, team]):
                violations[1] += 1

        violations[2] += len(gamesNeeded)

    return violations

def createRandomScheduleColumns(nrTeams):
    """Generates a randomly unpaired columnsFirst schedule

    Arguments:
        nrTeams (int) : The number of teams present in the schedule

    Returns:
        Schedule ([int, int]) : The randomly generated schedule generated
    """
        
    nrRounds = (2*nrTeams)-2
    schedule = np.full((nrRounds, nrTeams), None)
    choices = list(range(-nrTeams, nrTeams+1))
    choices.remove(0)

    for team in range(nrTeams):
        team += 1
        teamsToPick = copy.deepcopy(choices)
        teamsToPick.remove(team)
        teamsToPick.remove(-team)
        for round in range(nrRounds):
            choice = random.choice(teamsToPick)
            teamsToPick.remove(choice)

            schedule[round, team-1] = choice

    return schedule

def checkScheduleConstraintsRows(schedule, nrTeams):
    """Calculates the number of violations present in the rowsFirst schedule

    Arguments:
        schedule ([int, int]) : Schedule 

        nrTeams (int) : The number of teams present in the schedule

    Returns:
        violations ([int]) : The number of violations present in the schedule, in the format [maxStreak, No-repeat, Double round-robin]
    """

    nrRounds = (2*nrTeams)-2
    violations = [0, 0, 0, 0, 0]
    for team in range(nrTeams):
        homeStreak = 0
        awayStreak = 0
        gamesNeeded = []

        for i in range(1, nrTeams+1):
            if i != team+1:
                gamesNeeded.append(i)
                gamesNeeded.append(-i)

        for round in range(nrRounds):
            #Check maxStreak
            if schedule[round, team] > 0:
                awayStreak = 0
                homeStreak += 1
            else:
                awayStreak += 1
                homeStreak = 0
            if homeStreak > U or awayStreak > U:
                violations[0] += 1

            #Check noRepeat
            if round > 0:
                if abs(schedule[round, team]) == abs(schedule[round-1, team]):
                    violations[1] += 1

            #Check if the opponent also has the current team as opponent (matches are paired) (Never happens but is used to check validity of schedules)
            if team != abs(schedule[round, abs(schedule[round, team])-1])-1:
                violations[2] += 1
            if schedule[round, team] < 0 and schedule[round, abs(schedule[round, team])-1] < 0:
                violations[2] += 1
            if schedule[round, team] > 0 and schedule[round, abs(schedule[round, team])-1] > 0:
                violations[2] += 1

            #Check if the current team is playing against itself (Never occurs but is checked)
            if abs(schedule[round, team])-1 == team:
                violations[2] += 1

            # Check for doubleRoundRobin violations (Each team appears exactly twice in each column: once home, once away)
            if schedule[round, team] in gamesNeeded:
                gamesNeeded.remove(schedule[round, team])

        #Check for double round-robin violations
        violations[2] += len(gamesNeeded)

    return  violations

def createRandomScheduleRows(nrTeams):
    """Generates a randomly paired rowsFirst schedule

    Arguments:
        nrTeams (int) : The number of teams present in the schedule

    Returns:
        Schedule ([int, int]) : The randomly generated schedule generated
    """
        
    nrRounds = (2*nrTeams)-2
    schedule = np.full((nrRounds, nrTeams), None)
    choices = list(range(-nrTeams, nrTeams+1))
    choices.remove(0)

    for round in range(nrRounds):
        teamsToPick = choices.copy()
        for team in range(nrTeams):
            if schedule[round, team] == None:
                team += 1
                teamsToPick.remove(team)
                teamsToPick.remove(-team)
                choice = random.choice(teamsToPick)
                teamsToPick.remove(choice)
                teamsToPick.remove(-choice)
                if choice > 0:
                    schedule[round, team-1] = choice
                    schedule[round, choice-1] = -team
                else:
                    schedule[round, team-1] = choice
                    schedule[round, abs(choice)-1] = team

    return schedule

def createSchedules(nrTeams, n):
    """Generates n schedules and saves the violations of the schedules

    Arguments:
        n (int) : The number of schedules to generate

        nrTeams (int) : The number of teams present in the schedule

    Returns:
        TotalViolations ([int, int]) : The violations present in all n schedules
    """

    start=datetime.now()

    maxStreak1 = []
    repeat1 = []
    robin1 = []
    total1 = []

    for i in range(n):
        schedule = createRandomScheduleColumns(nrTeams)
        violations = checkScheduleConstraintsColumns(schedule, nrTeams)

        # schedule = createRandomScheduleRows(nrTeams)
        # violations = checkScheduleConstraintsRows(schedule, nrTeams)

        maxStreak = violations[0]
        repeat = violations[1]
        robin = violations[2]

        value = np.sum(violations)

        maxStreak1.append(maxStreak)
        repeat1.append(repeat)
        robin1.append(robin)
        total1.append(value)

    time = datetime.now()-start
    time = time.total_seconds()

    print(total1, robin1, maxStreak1, repeat1)
    print(time)

if int(sys.argv[1]) % 2 == 0:
    createSchedules(int(sys.argv[1]), int(sys.argv[2]))
else:
    print("n must be even")
