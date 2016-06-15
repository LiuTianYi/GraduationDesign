# -*- coding: utf-8 -*-
import math
import time
from operator import itemgetter
import random
from numpy.random.mtrand import shuffle

class User:
    'A class for user'
    
    def __init__(self, _id):
        self.id = _id
        self.profile = {}
    
    def getRandomValue(self):
        'Get random 0 or 1'
        if random.random() >= 0.5:
            return 1
        else:
            return 0
    
    def createProfile(self, features):
        'Create profile for user based on features'
        for f in features:
            self.profile[f] = self.getRandomValue()
            
    def getProfile(self):
        'Get the profile of user'
        if len(self.profile) == 0:
            return None
        return self.profile

class Item:
    'A class for item'
    
    def __init__(self, _id):
        self.id = _id
        self.content = {}
    
    def getRandomValue(self):
        'Get random 0 or 1'
        if random.random() >= 0.5:
            return 1
        else:
            return 0
        
    def createContentVector(self, features):
        'Create content vector'
        if len(self.content) > 0:
            return
        for f in features:
            self.content[f] = self.getRandomValue()
    
    def getContentVector(self):
        if len(self.content) == 0:
            return None
        return self.content

def getRawLog(N, user_amount, item_amount, features):
    'Get raw log'
    if N <= 0:
        return []
    
    raw_log = []
    all_user_dic = {}
    all_item_dic = {}
    
    for i in range(user_amount):
        user = User('user ' + str(i))
        user.createProfile(features)
        all_user_dic['user ' + str(i)] = user
    
    for j in range(item_amount):
        item = Item('item ' + str(j))
        item.createContentVector(features)
        all_item_dic['item ' + str(j)] = item
    
    moment = time.time()
    gap = 5
    j = 0
    for uid in all_user_dic.keys():
        for i in range(N):
            random_item = 'item ' + str((int)(random.random() * item_amount))
            random_time = moment + j * gap
            raw_log.append((uid, random_item, random_time))
            j += 1
    
    shuffle(raw_log)
    return raw_log, all_user_dic, all_item_dic

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

def getCorrelationOfVectors(user_profile, item_content):
    'calculate the correlation of vectors of user_profile and item_content'
    if user_profile == None or item_content == None:
        return None
    
    dot_product = 0.0
    user_len = 0.0
    item_len = 0.0
    
    for feature, value in user_profile.items():
        dot_product += value * item_content[feature]
        user_len += value * value
        item_len += item_content[feature] * item_content[feature]
    
    if user_len == 0 and item_len == 0:
        return 1.0
    
    if user_len == 0 or item_len == 0:
        count = 0.0
        for feature in user_profile.keys():
            if user_profile[feature] == item_content[feature]:
                count += 1
        return count / len(user_profile.keys())
    
    return dot_product / math.sqrt(user_len * item_len)

def getCorrelationOfVectors_v2(user_profile, item_content):
    'calculate the correlation of vectors of user_profile and item_content'
    if user_profile == None or item_content == None:
        return None
    
    correlation = 0.0
    
    for feature, value in user_profile.items():
        correlation += value * item_content[feature]
    
    return correlation / len(user_profile)

def recommendByContent(user, iteracted_items, all_item_dic, N):
    'recommend N items by the correlation of vectors of user profile and item content'
    if user == None or all_item_dic == None or len(all_item_dic) == 0 or N <= 0:
        return None
    
    recommend_list = {}
    
    for item_id, item in all_item_dic.items():
        if item_id not in iteracted_items.keys():
            correlation = getCorrelationOfVectors_v2(user.getProfile(), item.getContentVector())
            recommend_list[item_id] = correlation
    
    return sorted(recommend_list.items(), key=itemgetter(1), reverse=True)[0:N]

def displayRecommendList(recommend_list):
    if recommend_list == None or len(recommend_list) == 0:
        return None
    
    for item in recommend_list:
        print item
        
def getRandomValue():
    if random.random() >= 0.5:
        return 1
    else:
        return 0

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

def getDiversity(item_list, all_item_dic):
    'Get diversity from item list'
    item_list_len = len(item_list)
    diversity = 0.0
    for i in range(item_list_len):
        for j in range(i+1,item_list_len):
            i1 = item_list[i]
            i2 = item_list[j]
            diversity += getCorrelationOfVectors(all_item_dic[i1].getContentVector(), all_item_dic[i2].getContentVector())
            
    diversity = 1.0 - diversity / (0.5 * item_list_len * (item_list_len - 1))
    return diversity

def cross_validation(k, dataset, all_user_dic, all_item_dic, item_amount):
    'Calculate precision and recall on data set with k-fold cross validation'
    
    users = getUsers(dataset)
    all_recommend_items_set = set()
    avg_precision = 0.0
    avg_recall = 0.0
    avg_coverage = 0.0
    avg_popularity = 0.0
    avg_diveristy = 0.0
    
    part = len(dataset) / k
    for user in users:
        for turn in range(k):
            start = turn * part
            end = start + part
            train_set = dataset[0:start] + dataset[end:]
            test_set = dataset[start:end]
            
            user_items_records = getUserItemsRecords(train_set)
            item_users_records = getItemUsersRecords(train_set)
            
            N = 20
            
            if user_items_records.has_key(user) == False:
                recommend_list = []
            else:
                recommend_items = recommendByContent(all_user_dic[user], user_items_records[user], all_item_dic, N)
                recommend_list = []
                for i in recommend_items:
                    recommend_list.append(i[0])
                all_recommend_items_set = all_recommend_items_set.union(set(recommend_list))
                avg_popularity += getPopularity(recommend_list, item_users_records)
                avg_diveristy += getDiversity(recommend_list, all_item_dic)
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
    avg_diveristy = avg_diveristy / (len(users) * k)   
    print 'precision is %f, recall is %f, coverage is %f, diversity is %f, popularity is %f' % (avg_precision, avg_recall, avg_coverage, avg_diveristy, avg_popularity)


features = ['subject', 'time', 'place', 'lecturer']
raw_log, all_user_dic, all_item_dic = getRawLog(50, 50, 100, features)
cross_validation(5, raw_log, all_user_dic, all_item_dic, len(all_item_dic))