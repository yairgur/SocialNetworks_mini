import networkx as nx
import matplotlib.pyplot as plt
import linecache
from collections import Counter
import datetime
import main as m


THRESHOLD = 25
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
    comment = linecache.getline(filename, i + 6)[4:].strip().replace('\n', ' ')
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


# treshold to get those who got more than X votes
def create_cand_lst(votes_lst, treshold):
    votes_lst = sorted(votes_lst, key=lambda x: x.voted_for, reverse=False)
    how_many_voted_for = Counter(vote.voted_for for vote in votes_lst)
    votes = Counter(vote.name for vote in votes_lst)
    tuple_of_cand_voters = []
    votes_lst_per_votee = []
    iter = 0
    for vote in votes_lst:
        votes_lst_per_votee.append(vote)
        iter = iter+1
        if iter == how_many_voted_for[vote.voted_for]:
            if how_many_voted_for[vote.voted_for] > treshold and votes[vote.name] > treshold:
                votes_lst_per_votee.sort(key=lambda x: x.date)
                tuple_of_cand_voters.append((Voter(vote.voted_for, treshold+1, 0, vote.result, 0, 0, 0, [], 0, 0, 0, len(votes_lst_per_votee)), votes_lst_per_votee))
            #lst_of_voters.append(Voted_for(vote.voted_for, vote.result, votes_lst_per_votee))
            votes_lst_per_votee = []
            iter = 0
    return tuple_of_cand_voters


""" Create a list of voters with all info, only voters which voted more than "treshold" times """
def create_voters_lst(votes_lst, treshold):
    votes_lst = sorted(votes_lst, key=lambda x: x.name, reverse=False)
    iter = 0
    total_len = 0
    total_votes = 0
    res = []
    comment_lst = []
    votes = Counter(vote.name for vote in votes_lst)
    how_many_voted_for = Counter(vote.voted_for for vote in votes_lst)
    for vote in votes_lst:
        total_len = total_len + len(vote.comment)
        comment_lst.append((vote.choice, vote.comment, vote.voted_for))
        total_votes = total_votes+1
        iter = iter+1
        if iter==votes[vote.name]:
            if total_votes > treshold and how_many_voted_for[vote.voted_for] > treshold:
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


def voter_dic(votes_lst, voters_lst, THRESHOLD):
    res = {}
    i = 0
    for vote in votes_lst:
        for voter in voters_lst:
            if vote.name == voter.name and voter.total_votes > THRESHOLD:
                if vote.name in res.keys():
                    (res[vote.name])[1].append(vote)
                    i = i+1
                else:
                    i = i+1
                    res[vote.name] = (voter, [vote])
    print("number of action made (should be 10416) is", i)
    print("len of res is: ", len(res.items()))
    return res


def create_graph(cand_lst, voters_dic):
    G = nx.DiGraph()
    for cand in cand_lst:
        for vote_rec in cand[1]:
            if vote_rec.choice == "1":
                #G.add_edge(vote_rec.name, cand[0].name, color='b', weight=len(vote_rec.comment))
                G.add_edge(vote_rec.name, cand[0].name, color='b', weight=1)
            elif vote_rec.choice == "-1":
                #G.add_edge(vote_rec.name, cand[0].name, color='r', weight=len(vote_rec.comment))
                G.add_edge(vote_rec.name, cand[0].name, color='r', weight=-1)
            else:
                #G.add_edge(vote_rec.name, cand[0].name, color='y', weight=len(vote_rec.comment))
                G.add_edge(vote_rec.name, cand[0].name, color='y', weight=0)
    NDG = G.to_undirected()  # NDG for Non-Directed-Graph
    print(nx.info(G))
    return G, NDG

def paint_graph(G):
    colors = nx.get_edge_attributes(G, 'color').values()
    pos = nx.spring_layout(G)  # pos = nx.circular_layout(G)
    deg = dict(G.degree)
    nx.draw(G, pos,
            edge_color=colors,
            node_size=[v / 10 for v in deg.values()])
    """,with_labels=True)"""
    plt.show()
    print(nx.info(G))

def main():

    votes_lst = create_votes_lst()
    voters_lst = create_voters_lst(votes_lst, THRESHOLD)
    cand_lst = create_cand_lst(votes_lst, THRESHOLD)
    #print("Ratio of candidates to voters is: ", len(cand_lst), " voters size: ", len(voters_lst))
    """
    counter = 0
    for cand in cand_lst:
        if cand[0].total_votes > 0:
            counter = counter+1
    print("how many candidates are also voters? : ", counter)
    """
    voters_dic = voter_dic(votes_lst, voters_lst, THRESHOLD)
    G, NDG = create_graph(cand_lst, voters_dic)


    """ --------------------------- Paint the Graph - takes tons of time -----------------------------------"""
    #paint_graph(G)


    """ ------------------------- Components and Clustering --------------------------------"""
    print("Maximal component in G is: ",
         m.find_max_connected_components(NDG, components=[list(cc) for cc in nx.strongly_connected_components(G)]))

    print(m.show_clustering(G, 50))
    print(m.show_clustering(NDG, 50))

    """ ------------------------ Answer Research Question -----------------------------------"""

    res = m.corolation(voters_lst, m.get_median_of_votes_length(votes_lst))
    sum_weird = 0
    sum_bad = 0
    for info in res:
        if info[2] > 0.5:
            sum_bad = sum_bad + 1
        if info[4] > 0.5:
            sum_weird = sum_weird + 1
    print("% of bad voters are there? ", sum_bad/len(res))
    print("% weird voters are there? ", sum_weird / len(res))


    """ ----------------------- Power Law Of Degrees ----------------------------------------"""
    m.deg_dist(G)


    """ ------------------------------ check positiveness and negativeness --------------------------"""
    m.positive_voters(voters_lst, 0.8)
    m.negative_voters(voters_lst, 0.8)

if __name__ == '__main__':
    main()