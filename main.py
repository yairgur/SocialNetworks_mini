
import networkx as nx
import matplotlib.pyplot as plt
import linecache
import statistics
from scipy import sparse

ATTR_NUM = 8    # Number of attributes for each vote in the input file
file = open("wiki-RfA.txt", "r")
G = nx.DiGraph()
NDG = nx.Graph()


class Vote(object):
    def __init__(self, voter, voted_for, choice, result, year, date, comment):
        self.voter = voter
        self.voted_for = voted_for
        self.choice = choice
        self.result = result
        self.year = year
        self.date = date
        self.comment = comment


class Voter(object):
    def __init__(self, name, total_votes, avg_vote_len, is_elected, oppose_votes, support_votes, neutral_votes, comment_lst):
        self.name = name
        self.total_votes = total_votes
        self.avt_vote_len = avg_vote_len
        self.is_elected = is_elected
        self.oppose_votes = oppose_votes
        self.support_votes = support_votes
        self.neutral_votes = neutral_votes
        self.comment_lst = comment_lst


''' Helper function for parsing data from data-set '''
def count_lines(file):
    count = 0
    for line in file:
        count = count + 1
    file.seek(0)
    return count


''' Create object of type Vote '''
def create_vote(filename, i):
    voter = linecache.getline(filename, i)[4:].strip()
    voted_for = linecache.getline(filename, i + 1)[4:].strip()
    choice = linecache.getline(filename, i + 2)[4:].strip()
    result = linecache.getline(filename, i + 3)[4:].strip()
    year = linecache.getline(filename, i + 4)[4:].strip()
    date = linecache.getline(filename, i + 5)[4:].strip()
    comment = linecache.getline(filename, i + 6)[4:].strip()
    return Vote(voter, voted_for, choice, result, year, date, comment)


''' Create an sorted and iterable list of all the votes in the data-set, beside those without information about the voter'''
def create_votes_lst():
    line = 1
    sorted_votes_lst = []
    filename = "wiki-RfA.txt"
    num_of_lines = count_lines(file)
    while line < num_of_lines:
        vote = create_vote(filename, line)
        line = line + ATTR_NUM
        if vote.voter != "":     # ignoring votes without voter name
            sorted_votes_lst.append(vote)
    # possible sort in-place, using less memory  lst.sort(key=lambda x: x.voter, reverse=False)
    return sorted(sorted_votes_lst, key=lambda x: x.voter, reverse=False)


""" Create a list of voters with all info, only voters which voted more than "treshold" times """
def create_voters_lst(votes_lst, distinct_voter_lst, treshold):
    i = 0
    total_len = 0
    total_votes = 0
    res = []
    comment_lst = []
    for vote in votes_lst:
        if vote.voter == distinct_voter_lst[i]:
            total_votes=total_votes+1
            total_len=total_len+len(vote.comment)
            comment_lst.append((vote.choice, vote.comment))
        else:
            if total_votes>treshold:
                res.append(Voter(vote.voter, total_votes, total_len//total_votes, 0, 0, 0, 0, comment_lst))
            comment_lst = []
            i=i+1
            total_len=len(vote.comment)
            total_votes=0
    update_votes_for_voters(res)
    update_is_elected(votes_lst, res)
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


""" A method from StackOverFlow -- 
https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order"""
def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]


def distinct_voters_lst(votes_lst):
    lst = []
    for vote in votes_lst:
        lst.append(vote.voter)
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


def positive_voters(voters_lst, treshold):
    pos_voters = {}
    for voter in voters_lst:
        if voter.support_votes/voter.total_votes > treshold:
            pos_voters[voter.name] = voter.support_votes/voter.total_votes
    return pos_voters


def negative_voters(voters_lst, treshold):
    neg_voters = {}
    for voter in voters_lst:
        if voter.oppose_votes/voter.total_votes > treshold:
            neg_voters[voter.name] = voter.support_votes/voter.total_votes
    return neg_voters


def get_median_of_votes_length(votes_lst):
    lst = []
    for vote in votes_lst:
        lst.append(len(vote.comment))
    return statistics.median(lst)


""" Research question """
def corolation(voters_lst, median):
    res = []
    bad_long_comments = 0
    for voter in voters_lst:
        for comment in voter.comment_lst:
            if len(comment[1]) > voter.avt_vote_len and comment[0]=="-1" and len(comment[1]) > median:
                bad_long_comments=bad_long_comments+1
        if voter.oppose_votes != 0:
            res.append((voter.name, bad_long_comments, bad_long_comments/voter.oppose_votes))
        bad_long_comments = 0
    return res


""" Graph analysis and creation """
def create_graph(votes_lst, distinct_voters_lst, treshold):
    i = 0
    edges = []
    voted_lst = []
    for vote in votes_lst:
        if vote.voter == distinct_voters_lst[i]:
            voted_lst.append(vote.voted_for)
        else:
            edges.append((vote.voter, vote.voted_for, vote.choice, len(voted_lst)))
            voted_lst = [vote.voted_for]
            i = i+1
    for edge in edges:
        if edge[3] > treshold:
            if edge[2] == "1":
                    G.add_edge(edge[0], edge[1], color='b', weight=1, relation="support")
                    NDG.add_edge(edge[0], edge[1], color='b', weight=1, relation="support")
            elif edge[2] == "-1":
                    G.add_edge(edge[0], edge[1], color='r', weight=-1, relation="oppose")
                    NDG.add_edge(edge[0], edge[1], color='r', weight=-1, relation="oppose")
            else:
                G.add_edge(edge[0], edge[1], color='y', weight=0, relation="neutral")
                NDG.add_edge(edge[0], edge[1], color='y', weight=0, relation="neutral")


def plot_deg_dist(G):
    degrees = [G.degree(n) for n in G.nodes()]
    plt.hist(degrees)
    # all_degrees = nx.degree(G).values()
    # unique_deg = f7(all_degrees)
    # count_of_degrees = []
    # for deg in unique_deg:
     #    x = all_degrees.count(deg)
     #    count_of_degrees.append(x)

    # plt.plot(unique_deg, count_of_degrees, 'yo-')
    plt.show()


""" Helper function for deg_hist(G) - to show distribution of the degrees """
def degree_histogram_directed(G, in_degree=False, out_degree=False):
    """Return a list of the frequency of each degree value.

    Parameters
    ----------
    G : Networkx graph
       A graph
    in_degree : bool
    out_degree : bool

    Returns
    -------
    hist : list
       A list of frequencies of degrees.
       The degree values are the index in the list.

    Notes
    -----
    Note: the bins are width one, hence len(list) can be large
    (Order(number_of_edges))
    """
    nodes = G.nodes()
    if in_degree:
        in_degree = dict(G.in_degree())
        degseq=[in_degree.get(k,0) for k in nodes]
    elif out_degree:
        out_degree = dict(G.out_degree())
        degseq=[out_degree.get(k,0) for k in nodes]
    else:
        degseq=[v for k, v in G.degree()]
    dmax=max(degseq)+1
    freq= [ 0 for d in range(dmax) ]
    for d in degseq:
        freq[d] += 1
    return freq


def deg_dist(G):
    in_degree_freq = degree_histogram_directed(G, in_degree=True)
    out_degree_freq = degree_histogram_directed(G, out_degree=True)
    degrees = range(len(in_degree_freq))
    plt.figure(figsize=(12, 8))
    # Demonstrating power-law
    plt.loglog(range(len(in_degree_freq)), in_degree_freq, 'go-', label='in-degree')
    plt.loglog(range(len(out_degree_freq)), out_degree_freq, 'bo-', label='out-degree')
    plt.xlabel('Degrees')
    plt.ylabel('Number of nodes')
    plt.title("Degree distribution of RfA")


def show_clustering(G):
    for item in nx.clustering(G).items():
        print(item)
    print("Average clustering is: ", nx.average_clustering(G))


def find_max_connected_components(G):
    components = list(nx.connected_components(G))
    max = 0
    for comp in components:
        if len(comp) > max:
            max = len(comp)
    return (max, len(components))


def main():
    treshold = 1
    votes_lst = create_votes_lst()
    distinct_voter_lst = distinct_voters_lst(votes_lst)
    voters_lst = create_voters_lst(votes_lst, distinct_voter_lst, treshold)
    create_graph(votes_lst, distinct_voter_lst, treshold)
    # relation = nx.get_edge_attributes(G, "relation")
    colors = nx.get_edge_attributes(G, 'color').values()
    pos = nx.spring_layout(G)   # pos = nx.circular_layout(G)
    deg = dict(G.degree)
    """
    nx.draw(G, pos,
            edge_color=colors,
            node_size=[v * 10 for v in deg.values()])

    """
    """,with_labels=True)"""
    plt.show()



    plot_deg_dist(G)
    deg_dist(G)
    plt.show()

    #for i in voters_lst:
        #print(i.name, i.oppose_votes, i.neutral_votes, i.support_votes, i.total_votes, i.avt_vote_len, i.is_elected)
    #for i in corolation(voters_lst, get_median_of_votes_length(votes_lst)):
        #print(i[0], i[1], i[2])
    print(len(voters_lst))
    print(nx.info(G))
    print("Out of: %d voters, %d has a positive views in more than 80 precents of their votes.\n total of %f precents"
          % (len(voters_lst),  len(positive_voters(voters_lst, 0.8)), (len(positive_voters(voters_lst, 0.8))/len(voters_lst))))
    print("Out of: %d voters, %d has a negative views in more than 80 precents of their votes.\n total of %f precents"
          % (len(voters_lst), len(negative_voters(voters_lst, 0.8)),
             (len(negative_voters(voters_lst, 0.8)) / len(voters_lst))))
    print(nx.density(NDG))
    #show_clustering(NDG)
    print(nx.diameter(NDG))



if __name__ == '__main__':
    main()

