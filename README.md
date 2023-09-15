# data_model
for running the load test you need docker docker-compose and Python at least
before you can run docker-compose we need an image of the Metabase with the Clickhouse plugin so use the command below to tag a Metabase image
## Creating a Metabase Docker image with ClickHouse driver

You can use a convenience script `build_docker_image.sh`, which takes three arguments: Metabase version, ClickHouse driver version, and the desired final Docker image tag.

```bash
./build_docker_image.sh v0.44.6 0.8.3 my-metabase-with-clickhouse:v0.0.1
```

where `v0.44.6` is Metabase version, `0.8.3` is ClickHouse driver version, and `my-metabase-with-clickhouse:v0.0.1` being the tag.
after tagging the Metabase image you can run the command 
```bash
docker-compose up -d
```
to run the Clickhouse and the Metabase username and the password are set in the docker-compose file and is username and password in order.
after that, you can use Jupyter Notebook or the command 


```bash
python3 ./run.py
```
to populate tables with fake data it adds 2 Million posts and 1 seen posts.
one note I like to add here is that I combined the voted and skipped tables into one table to use less disk and it is easier to query and name it voted_skipped.
schema of the database is defined as 
```
CREATE TABLE default.post
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
SETTINGS index_granularity = 8192
```
```
CREATE TABLE default.voted_skipped
(
    `post_id` Int64,
    `user_Id` Int64,
    `action` Enum8('skipped' = 0, 'voted' = 1),
    `create_at` DateTime
)
ENGINE = MergeTree
ORDER BY create_at
SETTINGS index_granularity = 8192 
```
and the query to get the posts that haven't been seen by a user we can run the below query in the Metabase

```
SELECT *
FROM post
WHERE ID NOT IN (
    SELECT post_id
    FROM voted_skipped
    WHERE user_Id = 48
)
ORDER BY create_date 
LIMIT 20
```
after running the below query we can get the following report 
20 rows in set. Elapsed: 0.351 sec. Processed 4.00 million rows, 245.50 MB (11.40 million rows/s., 699.45 MB/s.)
Peak memory usage: 18.92 MiB.
as it shows it doesn't need a lot of memory and CPU to calculate the response and the disk gets used for saving the data as follows
```
┌─table───────────────────┬─size───────┬────rows─┬─days─┬─avgDaySize─┐
│ post                    │ 127.87 MiB │ 2000000 │    0 │ inf YiB    │
│ voted_skipped           │ 7.22 MiB   │ 1000000 │    0 │ inf YiB    │
```
so it shows that the Clickhouse is also disk efficient. <br />
for this amount of load, this solution going to work perfectly, and doing all the other work is kind of over-engineering. <br />
I like to summarize all the things I have told till now <br />
1-  Use a NoSQL database system, such as clickhouse that can handle large volumes of data and support horizontal scaling. NoSQL databases are more flexible and performant than relational databases for this use case, as they do not require complex joins or transactions, and can store data in a normalized. <br />
2- used only two tables as it is reasonable to combine vite and skip tables together  <br />


