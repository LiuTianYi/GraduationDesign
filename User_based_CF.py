# -*- coding: utf-8 -*-
import json
import urllib
import math
import time
import random
from operator import itemgetter
from numpy.random.mtrand import shuffle

def getRawData():
    'Get raw JSON-format data from the web page'
    page = urllib.urlopen("https://api.aminer.org/api/activity/all")
    content = page.read()
    raw_data = json.loads(content) # List-format inverted index of items
    return raw_data

def getRawLog(raw_data):
    'Get raw log-format data from raw JSON-format data'
    raw_log = []
    seconds = time.time()
    gap = 5
    i = 0
    for item in raw_data:
        for u in item['activityLike']:
            #like = 1
            raw_log.append((u, item['id'], seconds + gap * i))
            i += 1
    print len(raw_log)
    return raw_log

def autoGetRawLog(N, user_amount, item_amount):
    'Auto generate raw log'
    if N <= 0:
        return []
    
    raw_log = []
    moment = time.time()
    gap = 5
    j = 0
    for uid in range(user_amount):
        for i in range(N):
            random_item = 'item ' + str((int)(random.random() * item_amount))
            random_time = moment + j * gap
            raw_log.append(('user ' + str(uid), random_item, random_time))
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
    user_items_records = {}
    for record in raw_log:
        if user_items_records.has_key(record[0]) == False:
            user_items_records[record[0]] = {}
        user_items_records[record[0]][record[1]] = record[2]
    return user_items_records
    
def getItemUsersRecords(raw_log):
    'Get item-users records from raw log'
    item_users_records = {}
    for record in raw_log:
        if item_users_records.has_key(record[1]) == False:
            item_users_records[record[1]] = {}
        item_users_records[record[1]][record[0]] = record[2]
    return item_users_records

def getUserSimilarity(item_users_records, alpha):
    'Get user similarity table from item-users records'
    user_similarity_table = {}
    N = {}
    
    for item, users in item_users_records.items():
        for u in users.keys():
            if N.has_key(u) == False:
                N[u] = 0
            N[u] += 1
            
            if user_similarity_table.has_key(u) == False:
                user_similarity_table[u] = {}
            
            for v in users.keys():
                if u != v:
                    if user_similarity_table[u].has_key(v) == False:
                        user_similarity_table[u][v] = 0
                    user_similarity_table[u][v] += 1.0 / (math.log(1.0 + len(users)) * (1 + alpha * math.fabs(users[u] - users[v]))) # penalty for popular item
            
    for u, rel in user_similarity_table.items():
        for v, sim in rel.items():
            user_similarity_table[u][v] = sim / math.sqrt(N[u] * N[v])
    
    return user_similarity_table

def recommendByUserCF(user, user_items_records, user_similarity_table, beta, N):
    'Recommend N items for a user by User-based Collaborative Filtering method'
    recommend_list = {}
    iteracted_items = user_items_records[user]
    current_time = time.time()
    
    for u, sim in sorted(user_similarity_table[user].items(), key=itemgetter(1), reverse=True):
        for i, m in user_items_records[u].items():
            if i not in iteracted_items.keys():
                if recommend_list.has_key(i) == False:
                    recommend_list[i] = 0
                recommend_list[i] += sim / (1 + beta * math.fabs(current_time - m))
    
    return sorted(recommend_list.items(), key=itemgetter(1), reverse=True)[0:N]

def displayRecommendList(recommend_list):
    for item in recommend_list:
        print item

def getPrecision(recommend_list, real_list):
    'Get precision of recommendation'
    if len(recommend_list) == 0:
        return 0
    
    hit = 0.0
    for item in recommend_list:
        if item in real_list:
            hit += 1
    precision = hit / len(recommend_list)
    return precision

def getRecall(recommend_list, real_list):
    'Get recall of recommendation'
    if len(real_list) == 0:
        return 0
    
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
            user_similarity_table = getUserSimilarity(item_users_records, 0.9)
            
            N = 15
            
            if user_items_records.has_key(user) == False:
                recommend_list = []
            else:
                recommend_items = recommendByUserCF(user, user_items_records, user_similarity_table, 0.9, N)
                recommend_list = []
                for i in recommend_items:
                    recommend_list.append(i[0])
                all_recommend_items_set = all_recommend_items_set.union(set(recommend_list))
                avg_popularity += getPopularity(recommend_list, item_users_records)
            
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

#raw_data = getRawData()
#raw_log = getRawLog(raw_data)

N = 40
user_amount = 50
item_amount = 100
raw_log = autoGetRawLog(N, user_amount, item_amount)
cross_validation(5, raw_log, item_amount)                    