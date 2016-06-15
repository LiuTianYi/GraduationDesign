# -*- coding: utf-8 -*-
import random
import time
from operator import itemgetter
from numpy.random.mtrand import shuffle

def getRawLog(N, user_amount, item_amount):
    'Get raw log whose each record is (u, i, t)'
    if N <= 0:
        return []
    
    raw_log = []
    
    moment = time.time()
    gap = 5
    j = 0
    for u in range(user_amount):
        for i in range(N):
            random_i = 'item ' + str((int)(random.random() * item_amount))
            random_t = moment + gap * j
            raw_log.append(('user ' + str(u), random_i, random_t))
            j += 1
    
    shuffle(raw_log)
    return raw_log

def getUsers(raw_log):
    'Get all users from log'
    users = set()
    for record in raw_log:
        if record[0] not in users:
            users.add(record[0])
    return users

def getUserItemsRecords(raw_log):
    'Get user-items records from raw log'
    user_items = {}
    
    for u, i, t in raw_log:
        if user_items.has_key(u) == False:
            user_items[u] = {}
        user_items[u][i] = t
    
    return user_items

def getItemUsersRecords(raw_log):
    'Get item-users records from raw log'
    item_users = {}
    
    for u, i, t in raw_log:
        if item_users.has_key(i) == False:
            item_users[i] = {}
        item_users[i][u] = t
    
    return item_users

def createBipartiteGraph(raw_log):
    'Create a bipartite graph of users and items'
    graph = {}
    
    for u, i, m in raw_log:
        if graph.has_key(u) == False:
            graph[u] = {}
        graph[u][i] = m
        
        if graph.has_key(i) == False:
            graph[i] = {}
        graph[i][u] = m
    
    return graph

def randomWalk(graph, original_node, alpha, k):
    'Random walk on bipartite graph for k rounds'
    rank_graph = {}
    
    for node in graph.keys():
        if node == original_node:
            rank_graph[node] = 1
        else:
            rank_graph[node] = 0
    
    for round in range(k):
        for node, connection in graph.items():
            convey_value = rank_graph[node] * alpha
            rank_graph[node] -= convey_value
            for v in connection.keys():
                rank_graph[v] += convey_value / len(connection)

    return rank_graph

def isItem(node):
    'If the node is an item, return true'
    if node[0] == 'i':
        return True
    else:
        return False

def recommendByBipartiteGraph(user, iteracted_items, rank_graph, N):
    'Recommend N items for a user based on item probability on rank_graph'
    recommend_list = {}
    for node, p in rank_graph.items():
        if isItem(node) and iteracted_items.has_key(node) == False:
            recommend_list[node] = p
    return sorted(recommend_list.items(), key=itemgetter(1), reverse=True)[0:N]

def displayRecommendList(recommend_list):
    for item in recommend_list:
        print item

def getPrecision(recommend_list, real_list):
    'Get precision of recommendation'
    if len(recommend_list) == 0:
        return 0.0
    
    hit = 0.0
    for item in recommend_list:
        if item in real_list:
            hit += 1
    precision = hit / len(recommend_list)
    return precision

def getRecall(recommend_list, real_list):
    'Get recall of recommendation'
    if len(real_list) == 0:
        return 0.0
    
    hit = 0.0
    for item in recommend_list:
        if item in real_list:
            hit += 1
    recall = hit / len(real_list)
    return recall

def getPopularity(item_list, item_users_records):
    'Get popularity from item list'
    popularity = 0.0
    if len(item_list) == 0:
        return popularity
    for item in item_list:
        if item_users_records.has_key(item) == True:
            popularity += len(item_users_records[item])
    popularity /= len(item_list)
    return popularity

def cross_validation(k, dataset, item_amount):
    'Calculate precision and recall on data set with k-fold cross validation'
    
    users = getUsers(dataset)
    all_recommend_items_set = set()
    avg_precision = 0.0
    avg_recall = 0.0
    avg_coverage = 0.0
    avg_popularity = 0.0
    
    part = len(dataset) / k
    for user in users:
        for turn in range(k):
            start = turn * part
            end = start + part
            train_set = dataset[0:start] + dataset[end:]
            test_set = dataset[start:end]
            
            user_items_records = getUserItemsRecords(train_set)
            item_users_records = getItemUsersRecords(train_set)
            graph = createBipartiteGraph(train_set)
            
            alpha = 0.9
            r = 5
            rank_graph = randomWalk(graph, user, alpha, r)
            N = 20
            
            if user_items_records.has_key(user) == False:
                recommend_list = []
            else:
                recommend_items = recommendByBipartiteGraph(user, user_items_records[user], rank_graph, N)
                recommend_list = []
                for i in recommend_items:
                    recommend_list.append(i[0])

                all_recommend_items_set = all_recommend_items_set.union(set(recommend_list))
                avg_popularity += getPopularity(recommend_list, item_users_records)
            #displayRecommendList(recommend_list)
            
            test_user_items_records = getUserItemsRecords(test_set)
            if test_user_items_records.has_key(user) == False:
                real_list = []
            else:
                real_list = list(test_user_items_records[user].keys())
               
            precision = getPrecision(recommend_list, real_list)
            recall = getRecall(recommend_list, real_list)
            
            avg_precision += precision
            avg_recall += recall
        
        print 'recommend for %s : %s' % (user, recommend_list)
        
    avg_precision = avg_precision / (len(users) * k)
    avg_recall = avg_recall / (len(users) * k)
    avg_coverage = (len(all_recommend_items_set) * 1.0) / (item_amount * 1.0)
    avg_popularity = avg_popularity / (len(users) * k)    
    print 'precision is %f, recall is %f, coverage is %f, popularity is %f' % (avg_precision, avg_recall, avg_coverage, avg_popularity)

N = 50
user_amount = 50
item_amount = 100
raw_log = getRawLog(N, user_amount, item_amount)
cross_validation(5, raw_log, item_amount)