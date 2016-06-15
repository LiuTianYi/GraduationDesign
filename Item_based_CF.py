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
    gap = 2
    i = 0
    for item in raw_data:
        for u in item['activityLike']:
            #like = 1
            raw_log.append((u, item['id'], seconds + gap * i))
            i += 1
    #print len(raw_log)
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

def getItemSimilarity(user_items_records, alpha):
    'Get item similarity table from user-items records'
    item_similarity_table = {}
    N = {}
    
    for user, items in user_items_records.items():
        for i in items.keys():
            if N.has_key(i) == False:
                N[i] = 0
            N[i] += 1
            
            if item_similarity_table.has_key(i) == False:
                item_similarity_table[i] = {}
                
            for j in items.keys():
                if i != j:
                    if item_similarity_table[i].has_key(j) == False:
                        item_similarity_table[i][j] = 0
                    item_similarity_table[i][j] += 1.0 / (math.log(1.0 + len(items)) * (1 + alpha * math.fabs(items[i] - items[j]))) # penalty for crazy user
                    
    for i, rel in item_similarity_table.items():
        for j, sim in rel.items():
            item_similarity_table[i][j] = sim / math.sqrt(N[i] * N[j])
            
    return item_similarity_table

def recommendByItemCF(user, iteracted_items, item_similarity_table, beta, N):
    'Recommend N items for a user by Item-based Collaborative Filtering method'
    recommend_list = {}
    current_time = time.time()
    
    for item, m in iteracted_items.items():
        for sim_item, sim in item_similarity_table[item].items():
            if sim_item not in iteracted_items.keys():
                if recommend_list.has_key(sim_item) == False:
                    recommend_list[sim_item] = 0
                recommend_list[sim_item] += sim / (1 + beta * math.fabs(current_time - m))
            
    return sorted(recommend_list.items(), key=itemgetter(1), reverse=True)[0:N]

def displayRecommendList(recommend_list):
    'Display recommend_list'
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

def getDiversity(item_list, item_similarity_table):
    'Get diversity from item list'
    item_list_len = len(item_list)
    diversity = 0.0
    for i in range(item_list_len):
        for j in range(i+1,item_list_len):
            i1 = item_list[i]
            i2 = item_list[j]
            if item_similarity_table[i1].has_key(i2) == True:
                diversity += item_similarity_table[i1][i2]
    diversity = 1.0 - diversity / (0.5 * item_list_len * (item_list_len - 1))
    return diversity

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
    avg_diveristy = 0.0
    avg_popularity = 0.0
    
    part = len(dataset) / k
    for user in users:
        for turn in range(k):
            start = turn * part
            end = start + part
            train_set = dataset[0:start] + dataset[end:]
            test_set = dataset[start:end]
            
            item_users_records = getItemUsersRecords(train_set)
            user_items_records = getUserItemsRecords(train_set)
            item_similarity_table = getItemSimilarity(user_items_records, 0.9)
            
            N = 20
            
            if user_items_records.has_key(user) == False:
                recommend_list = []
            else:
                recommend_items = recommendByItemCF(user, user_items_records[user], item_similarity_table, 0.9, N)
                recommend_list = []
                for i in recommend_items:
                    recommend_list.append(i[0])
                avg_diveristy += getDiversity(recommend_list, item_similarity_table)
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
    avg_diveristy = avg_diveristy / (len(users) * k)
    avg_popularity = avg_popularity / (len(users) * k)    
    print 'precision is %f, recall is %f, coverage is %f, diversity is %f, popularity is %f' % (avg_precision, avg_recall, avg_coverage, avg_diveristy, avg_popularity)
    
#raw_data = getRawData()
#raw_log = getRawLog(raw_data)

N = 50
user_amount = 50
item_amount = 100
raw_log = autoGetRawLog(N, user_amount, item_amount)
cross_validation(5, raw_log, item_amount)