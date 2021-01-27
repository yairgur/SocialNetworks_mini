import networkx as nx
import matplotlib.pyplot as plt
import statistics
import numpy as np


""" A method from StackOverFlow -- 
https://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-whilst-preserving-order"""
def f7(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]




def positive_voters(voters_lst, treshold):
    pos_voters = {}
    avg_votes_plt = []
    for voter in voters_lst:
        if voter.support_votes / voter.total_votes > treshold:
            pos_voters[voter.name] = voter.support_votes  # /voter.total_votes
            avg_votes_plt.append(voter.avt_vote_len)
    plot_scatter(avg_votes_plt, list(pos_voters.values()), "AVG votes len for voter", "Positive votes",
                 "Positive votes depending on the AVG votes len of the voter")
    return pos_voters


def negative_voters(voters_lst, treshold):
    avg_votes_plt = []
    neg_voters = {}
    for voter in voters_lst:
        if voter.oppose_votes / voter.total_votes > treshold:
            neg_voters[voter.name] = voter.oppose_votes  # /voter.total_votes
            avg_votes_plt.append(voter.avt_vote_len)
    plot_scatter(avg_votes_plt, list(neg_voters.values()), "AVG votes len for voter", "Negative votes",
                 "Negative votes depending on the AVG votes len of the voter")
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
    weird_comment = 0
    bad_lst = []
    weird_lst = []
    voters_plt = []
    ratio_plt = []
    for voter in voters_lst:
        for comment in voter.comment_lst:
            if len(comment[1]) > voter.avt_vote_len and len(comment[1]) > median:
                if comment[0] == "-1":
                    bad_long_comments = bad_long_comments + 1
                else:
                    weird_comment = weird_comment+1
            # if bad_long_comments > 50:
        bad_lst.append(bad_long_comments)
        weird_lst.append(weird_comment)
        voters_plt.append(voter.avt_vote_len)
        if voter.oppose_votes != 0:
            ratio_plt.append(bad_long_comments / voter.oppose_votes)
            res.append((voter.name, bad_long_comments, bad_long_comments / voter.oppose_votes, weird_comment, weird_comment / (voter.support_votes+voter.neutral_votes)))
        else:
            ratio_plt.append(0)
        print("total recieved:", voter.name, voter.oppose_recieved, voter.neutral_recieved, voter.support_recieved,
              voter.total_recieved)

        bad_long_comments = 0
        weird_comment = 0

    plot_scatter(voters_plt, bad_lst, 'Avg comment length', 'Bad Comments',
                 "Bad Long Comments dependent on avg comment length")
    plot_scatter(voters_plt, weird_lst, 'Avg comment length', 'Weird Comments',
                 "Weird Comments dependent on avg comment length")

    return res


def plot_scatter(x, y, x_label, y_label, title):
    plt.plot(x, y, '.')
    plt.plot(np.unique(x), np.poly1d(np.polyfit(x, y, 1))(np.unique(x)))
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.title(title)
    plt.figure()
    plt.show()


def plot_deg_dist(G):
    all_degrees = [val for (node, val) in G.degree()]
    unique_deg = f7(all_degrees)
    count_of_degrees = []
    for deg in unique_deg:
        x = all_degrees.count(deg)
        count_of_degrees.append(x)

    plt.plot(unique_deg, count_of_degrees, 'yo-')
    plt.show()



def degree_histogram_directed(G, in_degree=False, out_degree=False):
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


def show_clustering(G, t1):
    max_co = 0
    x = []
    y = []
    sum = 0
    for node, value in nx.clustering(G).items():
        if nx.is_directed(G):
            in_deg = G.in_degree(node)
        else:
            in_deg = G.degree(node)
        if value > 0 and in_deg > t1:
            sum = sum+value
            x.append(in_deg)
            y.append(value)
            if value > max_co:
                max_co = value
            #print(in_deg, value)
    print("Average clusterigg is: ", nx.average_clustering(G))
    print("Average clusterigg for those who got more than t1 votes is: ", sum/len(x))
    print("Max clusterigg is: ", max_co)
    if nx.is_directed(G):
        plot_scatter(x, y, "In-Degrees", "Clustering co-efficient", "Clustering dependent on In-Degrees")
    else:
        plot_scatter(x, y, "Degrees", "Clustering co-efficient", "Clustering dependent on Degrees")



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




def main():

    """ ------------------- Positive and negative voters -----------------------
    
    ratio_negative = negative_voters(voters_lst, 0.8)
    ratio_positive = positive_voters(voters_lst, 0.8)
    print("ratio positive ", len(ratio_positive)/len(voters_lst))
    print("ratio negative ", len(ratio_negative) / len(voters_lst))
    #      % (len(voters_lst), len(negative_voters(voters_lst, 0.8)),
    #         (len(negative_voters(voters_lst, 0.8)) / len(voters_lst))))
    
        -------------------- Other things og Graphs -----------------------------------
    
    #for comp in componentsNDG:
     #   print("density of comp:",nx.density(comp))
    lst = show_clustering(NDG)
    print(type(lst))
    print("len of clustered", len(lst), " len of voters: ", len(voters_lst))
    lst = lst[:len(voters_lst)]
    
    #print(diameter_list(G, components))
    #print(diameter_list(NDG, componentsNDG))
    
    
    --------------------------- Density Area ----------------------------------------
    
    print(nx.density(NDG))
    print(nx.density(G))
    """

if __name__ == '__main__':
    main()