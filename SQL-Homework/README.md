# SQL Homework
The goal for this homework is to write queries to get information from a database using the psql command line client. We have the cooking 
stack exchange database set up on the machine csgpu1 with the user account cslab with permissions to perform SELECT queries on the Users 
and Posts tables. You can connect via one of the lab computers, which you can connect to via SSH. We will have an SSH tunnel set up for 
each of these machines so you can connect to the database as if it was hosted locally on that lab machine. 

## Homework Requirements
1. Run the following queries and turn in the result of running each along with a description of what you think the query is finding:
    - SELECT title FROM Posts WHERE posttypeid = 1 ORDER BY score DESC LIMIT 5;
    - SELECT reputation,displayname FROM users ORDER BY reputation DESC LIMIT 5;
    - SELECT displayname,ownerdisplayname FROM users
        INNER JOIN posts ON users.id = owneruserid
        WHERE displayname <> ownerdisplayname;
2. Construct queries to answer the following questions. Turn your query, the result, and a description of how your query works.
    - Find the question with the most tags.
    - How many questions were asked on a Friday.
    - Which month of the year sees the most activity.
3. Write three different queries of your own. Turn in the query, the result, and an English description of the information the query was accessing.
