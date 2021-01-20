import csv
import networkx as nx
import matplotlib.pyplot as plt
import linecache
import statistics
from collections import Counter
import datetime
import numpy as np


ATTR_NUM = 8    # Number of attributes for each vote in the input file
file = open("wiki-RfA.txt", "r")



class Vote(object):
    def __init__(self, name, voted_for, choice, result, date, comment):
        self.name = name
        self.voted_for = voted_for
        self.choice = choice
        self.result = result
        self.date = date
        self.comment = comment


class Voter(object):
    def __init__(self, name, total_votes, avg_vote_len, is_elected, oppose_votes, support_votes, neutral_votes, comment_lst, oppose_recieved, neutral_recieved, support_recieved, total_recieved):
        self.name = name
        self.total_votes = total_votes
        self.avt_vote_len = avg_vote_len
        self.is_elected = is_elected
        self.oppose_votes = oppose_votes
        self.support_votes = support_votes
        self.neutral_votes = neutral_votes
        self.comment_lst = comment_lst
        self.oppose_recieved = oppose_recieved
        self.neutral_recieved = neutral_recieved
        self.support_recieved = support_recieved
        self.total_recieved = total_recieved


class Voted_for(object):
    def __init__(self, voted_for, is_elected, voters_lst):
        self.voted_for = voted_for
        self.is_elected = is_elected
        self.voters_lst = voters_lst

''' Helper function for parsing data from data-set '''
def count_lines(file):
    count = 0
    for line in file:
        count = count + 1
    file.seek(0)
    return count


''' Create object of type Vote '''
def parse_vote(filename, i):
    name = linecache.getline(filename, i)[4:].strip()
    voted_for = linecache.getline(filename, i+1)[4:].strip()
    choice = linecache.getline(filename, i + 2)[4:].strip()
    result = linecache.getline(filename, i + 3)[4:].strip()
    date = linecache.getline(filename, i + 5)[4:].strip()
    if date != "":
        try:
            date = datetime.datetime.strptime(date, '%H:%M, %d %B %Y')
        except ValueError as e:
            try:
                date = datetime.datetime.strptime(date, '%H:%M, %d %b %Y')
            except ValueError as e:
                print("value error", date)
    else:
        date = datetime.datetime(2100, 12, 12, 12, 12) # if there is no date, it will be last
    comment = linecache.getline(filename, i + 6)[4:].strip()
    return Vote(name, voted_for, choice, result, date, comment)


''' Create an sorted and iterable list of all the votes in the data-set, beside those without information about the voter'''
def create_votes_lst():
    line = 1
    unsorted_votes_lst = []
    filename = "wiki-RfA.txt"
    num_of_lines = count_lines(file)
    while line < num_of_lines:
        vote = parse_vote(filename, line)
        line = line + ATTR_NUM
        if vote.name != "":     # ignoring votes without voter name
            unsorted_votes_lst.append(vote)
    # possible sort in-place, using less memory  lst.sort(key=lambda x: x.voter, reverse=False)
    return unsorted_votes_lst


def create_voted_for_lst(votes_lst):
    votes_lst = sorted(votes_lst, key=lambda x: x.voted_for, reverse=False)
    how_many_voted_for = Counter(vote.voted_for for vote in votes_lst)
    lst_of_voters = []
    votes_lst_per_votee = []
    iter = 0
    for vote in votes_lst:
        votes_lst_per_votee.append(vote)
        iter = iter+1
        if iter == how_many_voted_for[vote.voted_for]:
            votes_lst_per_votee.sort(key=lambda x: x.date)
            lst_of_voters.append(Voted_for(vote.voted_for, vote.result, votes_lst_per_votee))
            votes_lst_per_votee = []
            iter = 0
    return lst_of_voters


""" Create a list of voters with all info, only voters which voted more than "treshold" times """
def create_voters_lst(votes_lst, treshold):
    votes_lst = sorted(votes_lst, key=lambda x: x.name, reverse=False)
    iter = 0
    total_len = 0
    total_votes = 0
    res = []
    comment_lst = []
    votes = Counter(vote.name for vote in votes_lst)
    for vote in votes_lst:
        total_len = total_len + len(vote.comment)
        comment_lst.append((vote.choice, vote.comment, vote.voted_for))
        total_votes = total_votes+1
        iter = iter+1
        if iter==votes[vote.name]:
            if total_votes > treshold:
                res.append(Voter(vote.name, total_votes, total_len // total_votes, 0, 0, 0, 0, comment_lst, 0, 0, 0, 0))
            iter=0
            comment_lst = []
            total_len = 0
            total_votes = 0
    update_votes_for_voters(res)
    update_is_elected(votes_lst, res)
    update_recieved_votes(res)
    return res


""" Helper function for create_voters_list which update for each voter if he tried to be elected,
 and if he did, if he made it """
def update_is_elected(votes_lst, voters_lst):
    for vote in votes_lst:
        for voter in voters_lst:
            if voter.name == vote.voted_for:
                voter.is_elected = vote.result


""" Helper function for create_voters_lst,
 which update for each voter, how many votes he voted, and from what kind (support, oppose, neutral"""
def update_votes_for_voters(voters_lst):
    support = 0
    oppose = 0
    neutral = 0
    for voter in voters_lst:
        for choice in voter.comment_lst:
            if choice[0] == "1":
                support = support+1
            elif choice[0] == "-1":
                oppose = oppose+1
            else:
                neutral = neutral+1
        voter.support_votes = support
        voter.oppose_votes = oppose
        voter.neutral_votes = neutral
        support = 0
        oppose = 0
        neutral = 0


def update_recieved_votes(voters_lst):
    votes_against = {}
    votes_favor = {}
    votes_neutral = {}
    for voter in voters_lst:
            for comment in voter.comment_lst:
                if comment[0] == "1":
                    if comment[2] not in votes_favor.keys():
                        votes_favor[comment[2]] = 1
                    else:
                        votes_favor[comment[2]] = votes_favor[comment[2]] + 1
                elif comment[0] == "-1":
                    if comment[2] not in votes_against.keys():
                        votes_against[comment[2]] = 1
                    else:
                        votes_against[comment[2]] = votes_against[comment[2]] + 1
                else:
                    if comment[2] not in votes_neutral.keys():
                        votes_neutral[comment[2]] = 1
                    else:
                        votes_neutral[comment[2]] = votes_neutral[comment[2]] + 1
    for voter in voters_lst:
        if voter.name in votes_neutral.keys():
            voter.neutral_recieved = votes_neutral[voter.name]
        if voter.name in votes_against.keys():
            voter.oppose_recieved = votes_against[voter.name]
        if voter.name in votes_favor.keys():
            voter.support_recieved = votes_favor[voter.name]
        voter.total_recieved = voter.oppose_recieved + voter.neutral_recieved + voter.support_recieved


""" A method from StackOverFlow -- 
https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order"""
def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def distinct_voters_lst(votes_lst):
    lst = []
    for vote in votes_lst:
        lst.append(vote.name)
    return f7(lst)


def distinct_voted_for_lst(votes_lst):
    lst = []
    for vote in votes_lst:
        lst.append(vote.voted_for)
    return f7(lst)


# currently not needed - FixMe
def print_lst(lst):
    for i in lst:
        print(i)


def create_csv_file(voted_for_lst):
    with open("wiki-info.txt", 'w', newline='') as my_file:
        fieldnames = ['User Name', 'Choice', 'Date', 'Comment']
        writer = csv.DictWriter(my_file, delimiter='\t', fieldnames=fieldnames)
        fieldnames_cand = [' ', '  ']
        writer_cand = csv.DictWriter(my_file, delimiter='\t', fieldnames=fieldnames_cand)

        for candidate in voted_for_lst:
            writer_cand.writeheader()
            writer_cand.writerow({fieldnames_cand[0] : candidate.voted_for, fieldnames_cand[1] : candidate.is_elected})
            writer.writeheader()
            for vote in candidate.voters_lst:
                writer.writerow({fieldnames[0] : vote.name, fieldnames[1] : vote.choice, fieldnames[2] : vote.date, fieldnames[3] : vote.comment})




def main():
    votes_lst = create_votes_lst()
    voted_for_list = create_voted_for_lst(votes_lst)
    iter = 0
    print(voted_for_list[1].voted_for, voted_for_list[1].is_elected)
    #for i in range(len(voted_for_list[1].voters_lst)):
        #print(voted_for_list[1].voters_lst[i].name)
    print()
#    voters_lst = create_voters_lst(votes_lst, 0)
    create_csv_file(voted_for_list)



if __name__ == '__main__':
    main()