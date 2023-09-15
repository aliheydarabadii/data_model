#!/usr/bin/env python
# coding: utf-8

# In[ ]:





# In[5]:


import random
import string

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    # print("Random string of length", length, "is:", result_str)
    return result_str


# In[103]:


from clickhouse_driver import Client

CLICKHOUSE_CLOUD_HOSTNAME = 'localhost'
CLICKHOUSE_CLOUD_USER = 'username'
CLICKHOUSE_CLOUD_PASSWORD = 'password'
client = Client(host=CLICKHOUSE_CLOUD_HOSTNAME, port='9000', database='default', user=CLICKHOUSE_CLOUD_USER, password=CLICKHOUSE_CLOUD_PASSWORD)



# In[117]:


client.execute("""CREATE TABLE IF NOT EXISTS default.post
(
    `ID` Int64,
    `post_title` String,
    `post_description` String,
    `img_url` String,
    `create_date` DateTime
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(create_date)
ORDER BY ID
TTL create_date + toIntervalYear(7)
SETTINGS index_granularity = 8192""");
client.execute("""
CREATE TABLE IF NOT EXISTS default.voted_skipped
(
    `post_id` Int64,
    `user_Id` Int64,
    `action` Enum8('skipped' = 0, 'voted' = 1),
    `create_at` DateTime
)
ENGINE = MergeTree
ORDER BY create_at
SETTINGS index_granularity = 8192
""");


# In[112]:


import random
data=[]
import datetime

 
# using now() to get current time



for x in range(2000000):
    current_time = datetime.datetime.now()
    data.append({"ID":x, "post_title":get_random_string(random.randint(5, 20)),"post_description":get_random_string(random.randint(5, 20)),"img_url":get_random_string(random.randint(5, 20)),"create_date":current_time})
print(len(data),"test")
client.execute("INSERT INTO post FORMAT JSONEachRow", data)






# In[113]:


import random
data=[]
for x in range(1000000):
    data.append({"post_id":x,"user_Id":random.randint(1, 50),"action":random.randint(0, 1),"create_at":datetime.datetime.now()})
    data.append({"post_id":x,"user_Id":random.randint(51, 100),"action":random.randint(0, 1),"create_at":datetime.datetime.now()})
    data.append({"post_id":x,"user_Id":random.randint(100, 150),"action":random.randint(0, 1),"create_at":datetime.datetime.now()})

# In[114]:


client.execute("INSERT INTO voted_skipped FORMAT JSONEachRow", data)

