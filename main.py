import networkx as nx
import matplotlib.pyplot as plt
import linecache
import statistics
from collections import Counter
import numpy as np

"""---------------------------- What we want to check and analyse? ----------------------------"""
"""
1. If t1 (int) first votes to a candidate are in favor, what is the chances for wining?
2. If a candidate gets "bad vote" (according to the definition), in the first t1 votes, what his chances to lose? is it affect on the result?
3. Do the most popular (max total votes) are having the same voters? check in the graph
4. corolation - bad votes ratio
5. check cliques (people who voting for each other).
possible to check cliques of negative and positive in seperate
6. check how many bad votes which are in favor are they, and what is the ratio
7. positive voters and negative ones - treshold 80%


"""


def positive_voters(voters_lst, treshold):
    pos_voters = {}
    total_votes_plt = []
    for voter in voters_lst:
        if voter.support_votes / voter.total_votes > treshold:
            pos_voters[voter.name] = voter.support_votes  # /voter.total_votes
            total_votes_plt.append(voter.total_votes)
    plot_scatter(total_votes_plt, list(pos_voters.values()), "Total votes for voter", "Positive votes",
                 "Positive votes depending on the total votes of the voter")
    return pos_voters


def negative_voters(voters_lst, treshold):
    total_votes_plt = []
    neg_voters = {}
    for voter in voters_lst:
        if voter.oppose_votes / voter.total_votes > treshold:
            neg_voters[voter.name] = voter.oppose_votes  # /voter.total_votes
            total_votes_plt.append(voter.total_votes)
    plot_scatter(total_votes_plt, list(neg_voters.values()), "Total votes for voter", "Negative votes",
                 "Negative votes depending on the total votes of the voter")
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
    bad_lst = []
    voters_plt = []
    ratio_plt = []
    for voter in voters_lst:
        for comment in voter.comment_lst:
            if len(comment[1]) > voter.avt_vote_len and comment[0] == "-1" and len(comment[1]) > median:
                bad_long_comments = bad_long_comments + 1
            # if bad_long_comments > 50:
        bad_lst.append(bad_long_comments)
        voters_plt.append(voter.avt_vote_len)
        if voter.oppose_votes != 0:
            ratio_plt.append(bad_long_comments / voter.oppose_votes)
            res.append((voter.name, bad_long_comments, bad_long_comments / voter.oppose_votes))
        else:
            ratio_plt.append(0)
        print("total recieved:", voter.name, voter.oppose_recieved, voter.neutral_recieved, voter.support_recieved,
              voter.total_recieved)

        bad_long_comments = 0

    plot_scatter(voters_plt, bad_lst, 'Avg comment length', 'Bad Comments',
                 "Bad Long Comments dependent on avg comment length?")
    plot_scatter(ratio_plt, voters_plt, 'ratio bad/total oppose', 'Avg comment length',
                 "Ratio of bad Comments dependent on avg comment length")

    return res


def plot_scatter(x, y, x_label, y_label, title):
    plt.plot(x, y, '.')
    plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))(np.unique(x)))
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.figure()
    plt.show()


""" Graph analysis and creation """


def create_graph(G, NDG, voters_lst, treshold):
    for voter in voters_lst:
        if voter.total_votes > treshold:
            for comment in voter.comment_lst:
                if comment[0] == "1":
                    G.add_edge(voter.name, comment[2], color='b', weight=1, relation="support")
                    NDG.add_edge(voter.name, comment[2], color='b', weight=1, relation="support")
                elif comment[0] == "-1":
                    G.add_edge(voter.name, comment[2], color='r', weight=-1, relation="oppose")
                    NDG.add_edge(voter.name, comment[2], color='r', weight=-1, relation="oppose")
                else:
                    G.add_edge(voter.name, comment[2], color='y', weight=0, relation="neutral")
                    NDG.add_edge(voter.name, comment[2], color='y', weight=0, relation="neutral")


def plot_deg_dist(G):
    # degrees = [G.degree(n) for n in G.nodes()]
    # plt.hist(degrees)
    all_degrees = [val for (node, val) in G.degree()]
    # all_degrees = nx.degree(G)
    # print("yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy", all_degrees, "yyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")
    unique_deg = f7(all_degrees)
    count_of_degrees = []
    for deg in unique_deg:
        x = all_degrees.count(deg)
        count_of_degrees.append(x)

    plt.plot(unique_deg, count_of_degrees, 'yo-')
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
        degseq = [in_degree.get(k, 0) for k in nodes]
    elif out_degree:
        out_degree = dict(G.out_degree())
        degseq = [out_degree.get(k, 0) for k in nodes]
    else:
        degseq = [v for k, v in G.degree()]
    dmax = max(degseq) + 1
    freq = [0 for d in range(dmax)]
    for d in degseq:
        freq[d] += 1
    return freq


def deg_dist(G):
    in_degree_freq = degree_histogram_directed(G, in_degree=True)
    out_degree_freq = degree_histogram_directed(G, out_degree=True)
    degrees = range(len(in_degree_freq))
    plt.figure(figsize=(12, 8))
    plt.loglog(range(len(in_degree_freq)), in_degree_freq, 'go-', label='in-degree')
    plt.loglog(range(len(out_degree_freq)), out_degree_freq, 'bo-', label='out-degree')
    plt.xlabel('Degree')
    plt.ylabel('Frequency')
    plt.title("Degree distribution of RfA")


def show_clustering(G):
    lst = []
    for key, value in nx.clustering(G).items():
        print(key, value)
        lst.append((key, value))
    print("Average clustering is: ", nx.average_clustering(G))
    return lst  # .sort(key=lambda tup: tup[1])


def find_max_connected_components(G, components):
    max = 0
    for comp in components:
        if len(comp) > max:
            max = len(comp)
    return (max, len(components))


def diameter_list(G, components):
    dia_lst = []
    for comp in components:
        dia_lst.append(nx.diameter(comp))
    return dia_lst


def find_max_in_dic(lst):
    max = 0
    name = ""
    for key, value in lst.items():
        if value > max:
            max = value
            name = key
    return (name, max, len(lst))


def voter_tri(G, voters_lst):
    lst = []
    for voter in voters_lst:
        if voter.total_recieved > 60:
            lst.append(voter)
    lst_tri = []
    for voter in lst:
        for voter1 in lst:
            lst_tri.append()


def main():
    """
    G = nx.DiGraph()
    NDG = nx.Graph()
    treshold = 3
    votes_lst = create_votes_lst()

    create_graph(G, NDG, voters_lst, treshold)
    components = [list(cc) for cc in nx.strongly_connected_components(G)]
    componentsNDG = list(nx.connected_components(NDG))
    # relation = nx.get_edge_attributes(G, "relation")
    colors = nx.get_edge_attributes(G, 'color').values()
    pos = nx.spring_layout(G)   # pos = nx.circular_layout(G)
    deg = dict(G.degree)
    nx.draw(G, pos,
            edge_color=colors,
            node_size=[v / 10 for v in deg.values()])
    ,with_labels=True)
    #plt.show()
    #plot_deg_dist(NDG)
    #deg_dist(G)
    #plt.show()
    #for i in voters_lst:
        #print(i.name, i.oppose_votes, i.neutral_votes, i.support_votes, i.total_votes, i.avt_vote_len, i.is_elected)
    #for i in corolation(voters_lst, get_median_of_votes_length(votes_lst)): # here is corolation with bad comments - exhibit A
        #print(i[0], i[1], i[2])
    print(nx.info(G))
    #      % (len(voters_lst), len(negative_voters(voters_lst, 0.8)),
    #         (len(negative_voters(voters_lst, 0.8)) / len(voters_lst))))
    print(nx.density(NDG))
    print(nx.density(G))
    #for comp in componentsNDG:
     #   print("density of comp:",nx.density(comp))
    lst = show_clustering(NDG)
    print(type(lst))
    print("len of clustered", len(lst), " len of voters: ", len(voters_lst))
    lst = lst[:len(voters_lst)]
    plot_scatter([i[1] for i in lst], [voter.total_recieved for voter in voters_lst], "Clustering Value", "Total Votes Recieved", "Clustering dependent on total voted recieved")
    plot_scatter([i[1] for i in lst], [voter.oppose_recieved for voter in voters_lst], "Clustering Value", "Oppose Votes Recieved", "Clustering dependent on oppose voted recieved")
    plot_scatter([i[1] for i in lst], [voter.support_recieved for voter in voters_lst], "Clustering Value", "Support Votes Recieved", "Clustering dependent on support voted recieved")
    for item in lst[:len(voters_lst)]:
        print(item)
    print("The maximal component in the Directed Graph is: ", find_max_connected_components(G, components))
    #print("The maximal component in the Non-Directed-Graph is: ", find_max_connected_components(NDG, componentsNDG))
    #print(diameter_list(G, components))
    #print(diameter_list(NDG, componentsNDG))
    #print("The one who got the most votes support has: ", find_max_in_dic(favor))
    #print("The one who got the most votes oppose has: ", find_max_in_dic(against))
    ratio_negative = negative_voters(voters_lst, 0.8)
    ratio_positive = positive_voters(voters_lst, 0.8)
    print("ratio positive ", len(ratio_positive)/len(voters_lst))
    print("ratio negative ", len(ratio_negative) / len(voters_lst))
    """


if __name__ == '__main__':
    main()