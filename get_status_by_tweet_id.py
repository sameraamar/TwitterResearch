from __future__ import print_function

import tweepy
import getopt
import logging
import os
# import traceback
# third-party: `pip install tweepy`


#%%%


from os import walk
from os.path import split, splitext, join, exists

def select_files(root, files, extensions=[]):
    """
    simple logic here to filter out interesting files based on extensions
    """

    selected_files = []

    for file in files:
        #do concatenation here to get full path 
        full_path = join(root, file)
        ext = splitext(file)[1]

        if ext in extensions:
            selected_files.append(full_path)

    return selected_files

def build_recursive_dir_tree(path, ext=[]):
    """
    path    -    where to begin folder scan
    """
    selected_files = []

    for root, dirs, files in walk(path):
        selected_files += select_files(root, files, extensions=ext)

    return selected_files
    

#%%



# global logger level is configured in main()
Logger = None
consumer_key = "15RlnMoVeVYMZZ7B75atfHoeT"
consumer_secret = "C92Vv4p4DdeNpTtMMRgCB3SlZ2ZxGqhw3WKjniZluyCQFXbWWd"
access_key = "743159365381787648-cviHOEuYncAL1DGnkiKx5DW5PkloSbi"
access_secret = "f6vLHwcF5LJTKbAGoJWhYSAkOnF3m2r9KqPSwgT6QepTQ"

def get_tweet_id(line):
    '''
    Extracts and returns tweet ID from a line in the input.
    '''
    line = str(line).strip()
    
    #(tagid,_timestamp,_sandyflag) = line.split('\t')
    #(_tag, _search, tweet_id) = tagid.split(':')
    return line

def get_tweets_single(twapi, idfilepath):
    '''
    Fetches content for tweet IDs in a file one at a time,
    which means a ton of HTTPS requests, so NOT recommended.

    `twapi`: Initialized, authorized API object from Tweepy
    `idfilepath`: Path to file containing IDs
    '''
    # process IDs from the file
    with open(idfilepath, 'rb') as idfile:
        for line in idfile:
            tweet_id = get_tweet_id(line)
            if tweet_id == '':
                continue 
            
            Logger.debug('Fetching tweet for ID %s', tweet_id)
            try:
                tweet = twapi.get_status(tweet_id)
                print('%s,%s' % (tweet_id, tweet.text.encode('UTF-8')))
            except tweepy.TweepError as te:
                Logger.warn('Failed to get tweet ID %s: %s', tweet_id, te.message)
                # traceback.print_exc(file=sys.stderr)
        # for
    # with

def get_tweet_list(twapi, idlist):
    '''
    Invokes bulk lookup method.
    Raises an exception if rate limit is exceeded.
    '''
    # fetch as little metadata as possible
    tweets = twapi.statuses_lookup(id_=idlist, include_entities=False, trim_user=True)
    
    return tweets
    #for tweet in tweets:
    #    print('%s,%s' % (tweet.id, tweet.text.encode('UTF-8')))

def get_tweets_bulk(twapi, idfilepath):
    '''
    Fetches content for tweet IDs in a file using bulk request method,
    which vastly reduces number of HTTPS requests compared to above;
    however, it does not warn about IDs that yield no tweet.

    `twapi`: Initialized, authorized API object from Tweepy
    `idfilepath`: Path to file containing IDs
    '''    
    # process IDs from the file
    tweet_ids = list()
    with open(idfilepath, 'r') as idfile:
        for line in idfile:
            line = line.strip()
            tweet_id = get_tweet_id(line)
            Logger.debug('Fetching tweet for ID %s', tweet_id)
            # API limits batch size to 100
            tweet_ids.append(tweet_id)
            if len(tweet_ids) > 99:
                yield get_tweet_list(twapi, tweet_ids)
                tweet_ids = list()
    # process rump of file
    if len(tweet_ids) > 0:
        return get_tweet_list(twapi, tweet_ids)
        
    return []

#%%
#import logging

Logger = logging.getLogger()
fhandler = logging.FileHandler(filename='mylog.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
Logger.addHandler(fhandler)
Logger.setLevel(logging.DEBUG)


#%%
import codecs
import json

def downloadTweets(srcfile, dstfile):
    out = codecs.open(dstfile, 'wb', "utf-8")

    try:
        count = 0
        for tweets in get_tweets_bulk(api, srcfile):
            Logger.debug('length: ' + str(len(tweets)))
            for tweet in tweets:
                count += 1
                #status = status_list[0]
                json_str = json.dumps(tweet._json)
                out.write(json_str)
                out.write('\n')
            Logger.debug('tweets: ' + str(count))
        
        out.close()
    except Exception as e:
        out.close()
        raise


#%%
import time
import datetime 

current_time = datetime.datetime.now().time() 
print(current_time.isoformat())

sourceFolder = 'Sensing trending topics in Twitter'
targetFolder = 'Sensing trending topics in Twitter - tweets'

while True:
    txtfiles = build_recursive_dir_tree(sourceFolder, ext=['.txt'])
    jsonfiles = build_recursive_dir_tree(targetFolder, ext=['.json'])
    
    tmp = []
    for t in txtfiles:
        txt = splitext(t)[0] + '.json'
        txt = txt.replace(sourceFolder, targetFolder)
        if txt not in jsonfiles:
            tmp.append(t)
    
    if len(tmp) == 0 :
        print ('We are done!')
        continue
    else:
        print('still have ', len(tmp), ' files to go!')
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)
    
    
    filename = 'Sensing trending topics in Twitter//fa_cup/FACup_ids/5_5_2012_14_0.txt'
    
    for filename in tmp:
        print ('File: ', filename)
        dst = filename.replace('Sensing trending topics in Twitter', 'Sensing trending topics in Twitter - tweets')
        dst = splitext(dst)[0] + '.json'
        
        head, tail = split(dst) 
        if not exists(head):
            os.makedirs(head)
        
        try:
            downloadTweets(filename, dst)
        except Exception as e:
            os.remove(dst)
            sec = 5*60
            current_time = datetime.datetime.now().time() 
            print ('[', current_time.isoformat(), '] Going to sleep ', sec/60.0, ' minutes!\nException : ', e)
            time.sleep(sec)
            print ('Waking up!')
            