from flask import Flask, request
import sqlite3
import json
from sqlite3 import Error

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/posts')
def show_all_posts():
	conn = sqlite3.connect(r"articles.db")
	cur = conn.cursor()
	
	cur.execute('select id from articles')
	allIds = cur.fetchall()
	print(allIds) # all the post ids 

	post_vote_count = []
	for i in allIds:
		query = cur.execute('select count(post_id) from votes where post_id=\'%s\'' % (i[0]))
		num_of_votes = query.fetchall()[0][0]
		post_vote_count.append(num_of_votes)
	
	print(post_vote_count) # votes for each post id 

	allPosts = cur.execute('select title from articles').fetchall()
	print(allPosts)
	
	postDictList = []
	index = 0
	for post, id in zip(allPosts, allIds):
		postDict = {}
		postDict["post_id"] = id[0]
		postDict["body"] = post[0]
		postDict["vote_count"] = post_vote_count[index]
		postDictList.append(postDict)
		index += 1
	
	return "{'posts':" + json.dumps(postDictList) + "}"

@app.route('/login', methods=['POST'])
def login(username):
	return 'Ok!'

@app.route('/posts/vote')
def vote_for_post():
	post_id = request.args.get('post_id')
	username = request.args.get('username')

	conn = sqlite3.connect(r"articles.db")
	cur = conn.cursor()
	cur.execute('create table if not exists votes (post_id, username)')
	
	cur.execute('select id from articles')
	allIds = cur.fetchall()

	# check if valid post id is given
	extractedIds = []
	for i in allIds:
		extractedIds.append(i[0])

	if int(post_id) not in extractedIds:
		return '{"error": "Invalid post ID"}'

	# check if user has never voted for that post before
	query = cur.execute('select * from votes where post_id=\'%s\' and username=\'%s\'' % (post_id, username))
	if (len(query.fetchall()) == 0):
		voter = (post_id, username)
		insert_voter(conn, voter)
		query = cur.execute('select count(post_id) from votes where post_id=\'%s\'' % (post_id))
		post_vote_count = query.fetchall()[0][0]
		return "{'post_id': %s, 'vote_count': %s}" % (post_id, post_vote_count) 
	else:
		return '{"error": "User has voted for this post before"}'

def insert_voter(conn, voter):
	cur = conn.cursor()
	cur.execute('insert into votes(post_id, username) values(?,?)', voter)
	conn.commit()

@app.route('/posts/top')
def show_top_posts():
	count = int(request.args.get('count')) # the number of top posts to display
	print(type(count))
	
	conn = sqlite3.connect(r"articles.db")
	cur = conn.cursor()
	
	top_posts = {}
	cur.execute('select id from articles')
	allIds = cur.fetchall()

	extractedIds = []
	for i in allIds:
		extractedIds.append(i[0])

	for i in extractedIds:
		query = cur.execute('select count(post_id) from votes where post_id=\'%s\'' % (i))
		num_of_votes = query.fetchall()[0][0]
		top_posts[i] =  num_of_votes
		
	vote_counts = {k: v for k, v in sorted(top_posts.items(), key=lambda item: item[1], reverse=True)[:count]} # the top n posts where n = count
	print(vote_counts) # prints the top voted posts 

	postDictList = []
	for post_id,vote in vote_counts.items():
		postDict = {}
		postDict["post_id"] = post_id
		query = cur.execute('select title from articles where id=\'%s\'' % (post_id))
		body = query.fetchall()[0][0]
		postDict["body"] = body
		postDict["vote_count"] = vote
		postDictList.append(postDict)
	
	return "{'posts':" + json.dumps(postDictList) + "}"

app.run(host = '0.0.0.0')