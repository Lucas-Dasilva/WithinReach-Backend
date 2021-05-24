from __future__ import print_function
import sys
from datetime import datetime, timedelta
from flask import render_template, flash, redirect, url_for, request, session
from flask_sqlalchemy import sqlalchemy
from math import sin,cos, sqrt, atan2, radians, asin, pi

from sqlalchemy import func

from app import app, db
from app.forms import PostForm, SortForm, ReplyForm, LoginForm, RegistrationForm
from app.models import Post, Reply, User, reactedPost,reactedReply
from flask_login import current_user, login_user, logout_user, login_required
import requests, json
from flask_jsonpify import jsonify
from app import moment



@app.before_first_request
def initDB(*args, **kwargs):
    session.permanent = True
    db.create_all()


######################
####Post Handlers######
######################
@app.route('/createUser', methods=['POST'])
def createUser():
    if request.method == 'POST':
        jUser = request.get_json()
        
        if(User.query.get(jUser["user_id"])):
            print("User already exists")
            return ("User Already Exists", 200)
        else:    
            print("User Doesnt exists")
            newuser = User(id = jUser["user_id"])
            db.session.add(newuser)
            db.session.commit()
            return ("Ok", 200)

#Create Post: Creates new post
@app.route('/createPostHandler', methods=['POST'])
def createPostHandler():
    if request.method == 'POST':
        jPost = request.get_json()
        user_id = jPost['user_id']
        postBody = jPost['post_body']
        latitude = jPost['latitude']
        longitude = jPost['longitude']
        
        newpost = Post(body = postBody, latitude = latitude,longitude = longitude, user_id = user_id)
        db.session.add(newpost)
        db.session.commit()
    return ("Ok", 200)

@app.route('/createReplyHandler', methods=['POST'])
def createReplyHandler():
    if request.method == 'POST':
        jPost = request.get_json()
        user_id = jPost['user_id']
        postBody = jPost['post_body']
        post = jPost['post']
        
        newpost = Reply(body = postBody, post = post, user_id = user_id)
        db.session.add(newpost)
        db.session.commit()
        return ("Okay", 200)


# @app.route("/getLocation", methods = ['POST'])
# def locationHandler():
#     if request.method == 'POST':
#         location = request.get_json()
#     #Must be rounded to avoid calc_dist issues
#     session['latitude'] = round(location['latitude'],7)
#     session['longitude'] = round(location['longitude'],7)
#     return ("Okay", 200)

@app.route("/upvoteHandler", methods = ['POST'])
def upvoteHandler():
    if request.method == 'POST':
        reaction = request.get_json()
        user_id = reaction['user_id']
        post_id = reaction['post_id']
        post = Post.query.get(post_id)
        #User that made the post
        postOwner = User.query.get(post.user_id)
        #Current User
        user = User.query.get(user_id)
        found = False
        #Do this only if post does not belong to user
        if user.id != post.user_id:
            #Check if they have already reacted to other posts
            if user.reactions.count() > 0:
                for react in user.reactions:
                    #if current user has reacted to this post before
                    if react.post == post.id:
                        #If local user trys to unUpvote a post (Take it out of database)
                        if react.status == 1:
                            found = True
                            post.likes = post.likes - 1
                            postOwner.karma = postOwner.karma - 1
                            db.session.delete(react)
                        #If local user trys to up vote a post that is already downvote (Stays in database)
                        elif react.status == -1:
                            found = True
                            react.status = 1
                            postOwner.karma = postOwner.karma + 2
                            post.likes = post.likes + 2
            #If local user wants to upvote an unreacted to post(Not in database yet, So add it)
            if found == False:
                newReaction = reactedPost(post = post.id, status = 1, user_id = user.id)
                db.session.add(newReaction)
                post.likes = post.likes + 1
                postOwner.karma = postOwner.karma + 1
        db.session.commit()
        session.modified =  True
    return ("Okay", 200)

@app.route("/downvoteHandler", methods = ['POST'])
def downvoteHandler():
    if request.method == 'POST':
        reaction = request.get_json()
        user_id = reaction['user_id']
        post_id = reaction['post_id']
        post = Post.query.get(post_id)
        #User that made the post
        postOwner = User.query.get(post.user_id)
        #Current User
        user = User.query.get(user_id)
        found = False
        #Do this only if post does not belong to user
        if user.id != post.user_id:
            if user.reactions.count() > 0:
                for react in user.reactions:
                    if react.post == post.id:
                        #If local user trys to unUpvote a post (Take it out of database)
                        if react.status == -1:
                            found = True
                            post.likes = post.likes + 1
                            postOwner.karma = postOwner.karma + 1
                            db.session.delete(react)
                        #If local user trys to up vote a post that is already downvote (Stays in database)
                        elif react.status == 1:
                            found = True
                            react.status = -1
                            postOwner.karma = postOwner.karma - 2
                            post.likes = post.likes - 2
            #If local user wants to upvote an unreacted to post(Not in database yet, So add it)
            if found == False:
                newReaction = reactedPost(post = post.id, status = -1, user_id = user.id)
                db.session.add(newReaction)
                post.likes = post.likes - 1
                postOwner.karma = postOwner.karma - 1
        db.session.commit()
        session.modified =  True
    return ("Okay", 200)

#Allows user to like replies
@app.route("/upvotereplyHandler", methods = ['POST'])
def upVoteReplyHandler():
    if request.method == 'POST':
        reaction = request.get_json()
        user_id = reaction['user_id']
        reply_id = reaction['reply_id']
        reply = Reply.query.get(reply_id)
        #User that made the post
        replyOwner = User.query.get(reply.user_id)
        #Current User
        user = User.query.get(user_id)
        found = False
        #Do this only if reply does not belong to user
        if user.id != reply.user_id:
            #Check if they have already reacted to other replies
            if user.reactionsR.count() > 0:
                for react in user.reactionsR:
                    #if current user has reacted to this post before
                    if react.reply == reply.id:
                        #If local user trys to unUpvote a post (Take it out of database)
                        if react.status == 1:
                            found = True
                            reply.likes = reply.likes - 1
                            replyOwner.karma = replyOwner.karma - 1
                            db.session.delete(react)
                        #If local user trys to up vote a post that is already downvote (Stays in database)
                        elif react.status == -1:
                            found = True
                            react.status = 1
                            replyOwner.karma = replyOwner.karma + 2
                            reply.likes = reply.likes + 2
            #If local user wants to upvote an unreacted to post(Not in database yet, So add it)
            if found == False:
                newReaction = reactedReply(reply = reply.id, post = reply.post, status = 1, user_id = user.id)
                db.session.add(newReaction)
                reply.likes = reply.likes + 1
                replyOwner.karma = replyOwner.karma + 1
        db.session.commit()
    return ("Okay", 200)

#Allows users to dislike replies, if a reply gets less than 5 likes then it gets deleted
@app.route("/downvotereplyHandler", methods = ['POST'])
def downVoteReplyHandler():
    if request.method == 'POST':
        reaction = request.get_json()
        user_id = reaction['user_id']
        reply_id = reaction['reply_id']
        reply = Reply.query.get(reply_id)
        #User that made the post
        replyOwner = User.query.get(reply.user_id)
        #Current User
        user = User.query.get(user_id)
        found = False
        #Do this only if reply does not belong to user
        if user.id != reply.user_id:
            if user.reactionsR.count() > 0:
                for react in user.reactionsR:
                    if react.reply == reply.id:
                        #If local user trys to unUpvote a reply (Take it out of database)
                        if react.status == -1:
                            found = True
                            reply.likes = reply.likes + 1
                            replyOwner.karma = replyOwner.karma + 1
                            db.session.delete(react)
                        #If local user trys to up vote a reply that is already downvote (Stays in database)
                        elif react.status == 1:
                            found = True
                            react.status = -1
                            replyOwner.karma = replyOwner.karma - 2
                            reply.likes = reply.likes - 2
            #If local user wants to upvote an unreacted to reply(Not in database yet, So add it)
            if found == False:
                newReaction = reactedReply(reply = reply.id, post = reply.post, status = -1, user_id = user.id)
                db.session.add(newReaction)
                reply.likes = reply.likes - 1
                replyOwner.karma = replyOwner.karma - 1
        db.session.commit()
        session.modified =  True
    return ("Okay", 200)


######################
####Get Requests######
######################
@app.route("/getUser/<user_id>", methods = ['GET'])
def getUser(user_id):
    if request.method == 'GET':
        if (User.query.get(user_id)):
            user = User.query.get(user_id)
            return jsonify(user.serialize())
        else:
            return("User Not yet Created")

#Posts whithin distance and sorted by time
@app.route("/getPosts/<latitude>/<longitude>/<user_id>", methods = ['GET'])
def getPosts(latitude, longitude, user_id):
    if request.method == 'GET':
        return (filterPosts(latitude,longitude, 1, user_id))

#Posts whithin distance and sorted by Likes
@app.route("/getPostsSorted/<latitude>/<longitude>/<user_id>", methods = ['GET'])
def getPostsSorted(latitude, longitude, user_id):
    if request.method == 'GET':
        return (filterPosts(latitude,longitude, 0, user_id))


@app.route("/getReplys/<post_id>/<user_id>", methods = ['GET'])
def getReplys(post_id,user_id):
    if request.method == 'GET':
        #Get Single Post
        post = Post.query.get(post_id)
        post_reactions = reactedPost.query.filter(user_id == reactedPost.user_id)
        #Get replys for for post
        replys = Reply.query.filter(post_id == Reply.post) #Filtering out replys that belong to post
        replys = replys.order_by(Reply.timestamp.desc()) #Sorting it by time
        reactions = reactedReply.query.filter(user_id == reactedReply.user_id) #filtering reply reactions by local user
        jReplys = jsonify(post=post.serialize(), 
                        post_reactions=[i.serialize() for i in post_reactions],
                        reply_list=[i.serialize() for i in replys],
                        react_list=[i.serialize() for i in reactions])
        return (jReplys)
        
@app.route("/getSinglePost/<post_id>/<user_id>", methods = ['GET'])
def getSinglePost(post_id, user_id):
    if request.method == 'GET':
        post = Post.query.get(post_id)
        reactions = reactedPost.query.filter(user_id == reactedPost.user_id)
        if(post):
            jPosts = jsonify(post=[post.serialize()], react_list=[i.serialize() for i in reactions])
            #print(jPosts)
            return (jPosts)


@app.route("/getReactions/<user_id>", methods = ['GET'])
def getReactions(user_id):
    reactions = reactedPost.query.filter(user_id == reactedPost.user_id)
    jReact = jsonify(react_list=[i.serialize() for i in reactions])
    #print(jReact)
    return (jReact)

@app.route("/getReplyReactions/<user_id>", methods = ['GET'])
def getReplyReactions(user_id):
    reactions = reactedReply.query.filter(user_id == reactedReply.user_id)
    jReact = jsonify(react_list=[i.serialize() for i in reactions])
    #print(jReact)
    return (jReact)


def filterPosts(latitude,longitude, sort, user_id):
    #Sort posts by time
    if (sort==1):
        posts = Post.query.order_by(Post.timestamp.desc())
    #Sort by likes
    else:
        posts = Post.query.order_by(Post.likes.desc())
    post_list = []
    #Posts that are in the distance radius
    posts_whithin_reach = 0

    #Scrolls through posts within a 1.5 mile to 10 mile radius
    #depending on post volume, the geo-based radius can expand to a 10 mile ring
    for i in posts:
        dist = distance(i.latitude,i.longitude, latitude, longitude)
        #1.5 Mile Radius
        if(dist < 1.5):
            posts_whithin_reach += 1
            objPost = i.serialize()
            objPost["distance"] = dist
            post_list.append(objPost)
    #Checking if there is enough posts in radius. Min=5 Posts
    #Yep
    if (posts_whithin_reach <= 10):
        posts_whithin_reach = 0
        post_list = []
        for i in posts:
            dist = distance(i.latitude,i.longitude, latitude, longitude)
            #Three Mile Radius
            if(dist < 3):
                posts_whithin_reach += 1
                objPost = i.serialize()
                objPost["distance"] = dist
                post_list.append(objPost)   
    #Checking if there still isn't enough posts, so expand the radius
    if (posts_whithin_reach <= 10):
        posts_whithin_reach = 0
        post_list = []
        for i in posts:
            dist = distance(i.latitude,i.longitude, latitude, longitude)
            #Five Mile Radius
            if(dist < 5):
                posts_whithin_reach += 1
                objPost = i.serialize()
                objPost["distance"] = dist
                post_list.append(objPost)  
    #If there is an abundance of posts, the delete the oldest ones 
    if (posts_whithin_reach >= 25):
         for i in posts:
            #Check if post is older than 10 days
            time_passed = datetime.utcnow() -  i.timestamp 
            if (time_passed.days > 7):
                deleteOldPost(i)
    #Merging reaction list with posts
    reactions = reactedPost.query.filter(user_id == reactedPost.user_id)
    #Setting new Post list
    if (post_list != []):
        jPosts = jsonify(post_list = post_list, react_list=[i.serialize() for i in reactions])
        return (jPosts)
    else:
        jPosts = jsonify(post_list = [], react_list=[i.serialize() for i in reactions])
        return (jPosts)


#Calc Distance for rest-api
def distance(lat1, lon1, lat2, lon2): 
    lat2 = float(lat2)
    lon2 = float(lon2)
    p = pi/180
    a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
    dist= 7917.6 * asin(sqrt(a)) #2 * Radius of earth in miles(3958.8) * asin
    # print("Distance:" + str(dist))
    return round(dist, 2)

# Delete post
def deleteOldPost(post):
    print("deleting post #" + str(post.id))
    #Deleting reply reactions
    for reaction in reactedReply.query.all():
        if (reaction.post == post.id):
            db.session.delete(reaction)
    #Deleting replys
    for reply in Reply.query.all():
        if (reply.post == post.id):
            db.session.delete(reply)
    #Deleting post reactions
    for reaction in reactedPost.query.all():
        if (reaction.post == post.id):
            db.session.delete(reaction)
    #Deleting Posts
    db.session.delete(post)
    db.session.commit()



######################
####WebApp Code######
######################
#Main home page: Sorts, only displays nearby posts@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    #yeetcount is number of posts
    sortForm = SortForm()
    user = User.query.get(current_user.id)
    totalReactions = user.reactions.count()

    #if position has changed update User database location 
    #session is float, user and post model is string
    if str(session["latitude"]) != user.latitude:
        user.latitude = str(session["latitude"])
        user.longitude = str(session["longitude"])
        db.session.commit()
    try: 
        user.latitude = str(session["latitude"])
        user.longitude = str(session["longitude"])
        for p in Post.query.all():
            calc_dist(p.id,user)
        db.session.commit()
    except:
        print("Unable to update session location")
    #Get the post with the most number of likes
    topPost = db.session.query(func.max(Post.likes)).scalar()

    if request.method == 'POST':
        # option = 1
        option = int(sortForm.sort.data)
        #print("option:", option)
        if (option == 1):
            posts = Post.query.order_by(Post.likes.desc())
        else:
            posts = Post.query.order_by(Post.timestamp.desc())
    else: 
        posts = Post.query.order_by(Post.timestamp.desc())

    return render_template('index.html', title="Welcome to Within Reach", posts= posts, postCount =  posts.count(), sortform = sortForm, user = user, totalReactions = totalReactions, topPost = topPost) 


#Calculate Distance of user to other posts 
def calc_dist(post_id,user):

    #Radius of earth in miles
    R = 3958.8
    post = Post.query.get(post_id)

    #Posts locations
    lat1 = radians(float(post.latitude))
    lon1 = radians(float(post.longitude))
    #Users location coordinates with session
    lat2 = radians(session['latitude'])
    lon2 = radians(session['longitude'])
    dlon = (lon2) - (lon1)
    dlat = (lat2) - (lat1)

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    #Dict Key has value of (distance from post, if post is upVoted, downVoted, or None)
    session[str(post_id)] = distance
    if post.user_id != user.id:
        try:
            dist = 2
            dist._user = user
            dist._post = post
            db.session.add(dist)
            db.session.commit()
        except:
            db.session.rollback()
    # for p in userDistance.query.all():
    #     if p.id != :
    #         p.distance = 3.4
    #         db.session.commit()
    #add distance to the db colummn, in order to sort it out
    #print(distance)
    
 
    return render_template('index.html')


#Create Post: Creates new post
@app.route('/postmsg', methods=['GET', 'POST'])
@login_required
def createpost():
    tempPost = PostForm()
    if tempPost.validate_on_submit():
        if (tempPost.body.data is not None):
            newpost = Post(body = tempPost.body.data, latitude = session['latitude'],longitude = session['longitude'], user_id = current_user.id)
            db.session.add(newpost)
            db.session.commit()
            postCount = Post.query.count()            
            #flash('New Post created!')
            return redirect(url_for('index'))
    return render_template('create.html', form = tempPost)


#Allows user to like posts
@app.route('/postLike/<post_id>/<ref>', methods=['GET'])
@login_required
def upVote(post_id, ref):
    post = Post.query.get(post_id)
    #User that made the post
    postOwner = User.query.get(post.user_id)
    #Current User
    user = User.query.get(current_user.id)
    found = False
    #Do this only if post does not belong to user
    if user.id != post.user_id:
        #Check if they have already reacted to other posts
        if user.reactions.count() > 0:
            for react in user.reactions:
                #if current user has reacted to this post before
                if react.post == post.id:
                    #If local user trys to unUpvote a post (Take it out of database)
                    if react.status == 1:
                        found = True
                        post.likes = post.likes - 1
                        postOwner.karma = postOwner.karma - 1
                        db.session.delete(react)
                    #If local user trys to up vote a post that is already downvote (Stays in database)
                    elif react.status == -1:
                        found = True
                        react.status = 1
                        postOwner.karma = postOwner.karma + 2
                        post.likes = post.likes + 2
        #If local user wants to upvote an unreacted to post(Not in database yet, So add it)
        if found == False:
            newReaction = reactedPost(post = post.id, status = 1, user_id = user.id)
            db.session.add(newReaction)
            post.likes = post.likes + 1
            postOwner.karma = postOwner.karma + 1
    db.session.commit()
    session.modified =  True
    if ref == "1":
        return redirect(url_for('comments', post_id=post_id))
    else:
        return redirect(url_for('index', post=post))

   

    

#Allows users to dislike posts, if a post gets less than 5 likes then it gets deleted
@app.route('/postDislike/<post_id>/<ref>', methods=['GET'])
@login_required
def downVote(post_id, ref):
    post = Post.query.get(post_id)
    #User that made the post
    postOwner = User.query.get(post.user_id)
    #Current User
    user = User.query.get(current_user.id)
    found = False

    #Do this only if post does not belong to user
    if user.id != post.user_id:
        if user.reactions.count() > 0:
            for react in user.reactions:
                if react.post == post.id:
                    #If local user trys to unUpvote a post (Take it out of database)
                    if react.status == -1:
                        found = True
                        post.likes = post.likes + 1
                        postOwner.karma = postOwner.karma + 1
                        db.session.delete(react)
                    #If local user trys to up vote a post that is already downvote (Stays in database)
                    elif react.status == 1:
                        found = True
                        react.status = -1
                        postOwner.karma = postOwner.karma - 2
                        post.likes = post.likes - 2
        #If local user wants to upvote an unreacted to post(Not in database yet, So add it)
        if found == False:
            newReaction = reactedPost(post = post.id, status = -1, user_id = user.id)
            db.session.add(newReaction)
            post.likes = post.likes - 1
            postOwner.karma = postOwner.karma - 1
    db.session.commit()
    session.modified =  True
    if ref == "1":
        return redirect(url_for('comments', post_id=post_id))
    else:
        return redirect(url_for('index', post=post))
  
@app.route('/postcomments/<post_id>', methods=['GET', 'POST'])
@login_required
def comments(post_id):
    #Original post to stay at the top
    post = Post.query.get(post_id)
    user = User.query.get(current_user.id)
    totalReactions = user.reactionsR.count()
    #Check if there any replies to the post
            
    form = ReplyForm()
    if form.validate_on_submit():
        if (form.body.data is not None):
            newreply = Reply(body = form.body.data, post = post_id, user_id = current_user.id)
            db.session.add(newreply)
            db.session.commit()
            #flash('New Reply created!')
            replys = Reply.query.order_by(Reply.timestamp.desc())

    else: 
        replys = Reply.query.order_by(Reply.timestamp.desc())

    return render_template('comments.html', post= post, user = user, form = form, totalReactions = totalReactions, replys = replys.filter(post_id == Reply.post))

#Allows user to like replies
@app.route('/replyLike/<reply_id>', methods=['GET'])
@login_required
def upVoteReply(reply_id):
    reply = Reply.query.get(reply_id)
    #User that made the reply
    replyOwner = User.query.get(reply.user_id)
    #Current User
    user = User.query.get(current_user.id)
    post = reply.post

    found = False
    #Do this only if reply does not belong to user
    if user.id != reply.user_id:
        #Check if they have already reacted to other replies
        if user.reactionsR.count() > 0:
            for react in user.reactionsR:
                #if current user has reacted to this post before
                if react.reply == reply.id:
                    #If local user trys to unUpvote a post (Take it out of database)
                    if react.status == 1:
                        found = True
                        reply.likes = reply.likes - 1
                        replyOwner.karma = replyOwner.karma - 1
                        db.session.delete(react)
                    #If local user trys to up vote a post that is already downvote (Stays in database)
                    elif react.status == -1:
                        found = True
                        react.status = 1
                        replyOwner.karma = replyOwner.karma + 2
                        reply.likes = reply.likes + 2
        #If local user wants to upvote an unreacted to post(Not in database yet, So add it)
        if found == False:
            newReaction = reactedReply(reply = reply.id, status = 1, user_id = user.id)
            db.session.add(newReaction)
            reply.likes = reply.likes + 1
            replyOwner.karma = replyOwner.karma + 1
    db.session.commit()
    session.modified =  True
    return redirect(url_for('comments', post_id = post))

#Allows users to dislike replies, if a reply gets less than 5 likes then it gets deleted
@app.route('/replyDislike/<reply_id>', methods=['GET'])
@login_required
def downVoteReply(reply_id):
    reply = Reply.query.get(reply_id)
    #User that made the post
    replyOwner = User.query.get(reply.user_id)
    #Current User
    user = User.query.get(current_user.id)
    post = reply.post

    found = False

    #Do this only if reply does not belong to user
    if user.id != reply.user_id:
        if user.reactionsR.count() > 0:
            for react in user.reactionsR:
                if react.reply == reply.id:
                    #If local user trys to unUpvote a reply (Take it out of database)
                    if react.status == -1:
                        found = True
                        reply.likes = reply.likes + 1
                        replyOwner.karma = replyOwner.karma + 1
                        db.session.delete(react)
                    #If local user trys to up vote a reply that is already downvote (Stays in database)
                    elif react.status == 1:
                        found = True
                        react.status = -1
                        replyOwner.karma = replyOwner.karma - 2
                        reply.likes = reply.likes - 2
        #If local user wants to upvote an unreacted to reply(Not in database yet, So add it)
        if found == False:
            newReaction = reactedReply(reply = reply.id, status = -1, user_id = user.id)
            db.session.add(newReaction)
            reply.likes = reply.likes - 1
            replyOwner.karma = replyOwner.karma - 1
    db.session.commit()
    session.modified =  True
    return redirect(url_for('comments', post_id=post))

@app.route('/register', methods=['GET', 'POST'])
def register():
    # latitude = session["latitude"], longitude = session["longitude"]
        #If user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
        flash('Registered!')

    return render_template('register.html', title='Register', form=form)

#Upon logging in, users location is saved to session, but only gets saved unto database, upon entering index
@app.route('/login', methods=['GET', 'POST'])
def login():
    #If user is already authenticated
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        #If user can't be found in database or password is wrong
        if user is None or not user.get_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        else:
            login_user(user, remember=form.remember_me.data)
            # flash("Location saved to session!")
            return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Delete post
@app.route('/delete/<post_id>', methods=['POST', 'DELETE'])
@login_required
def delete(post_id):
    thepost = Post.query.get(post_id)
    allPosts = userDistance.query.all()
    for post in allPosts:

        if post.post_id == int(post_id):
            db.session.delete(post)
            db.session.commit()

    db.session.delete(thepost)
    flash('Post deleted.')
    db.session.commit()
    return redirect(url_for('index', thepost = thepost))

#Edit post by deleting current post and replacing with new post
@app.route('/edit/<post_id>', methods=['GET', 'POST'])
@login_required
def edit(post_id):
    tempPost = PostForm()
    thepost = Post.query.get(post_id)
    db.session.delete(thepost)
    if tempPost.validate_on_submit():
        if (tempPost.body.data is not None):
            newpost = Post(body = tempPost.body.data, latitude = session['latitude'],longitude = session['longitude'], user_id = current_user.id)
            db.session.add(newpost)
            db.session.commit()
            postCount = Post.query.count()            
            flash('Post edited!')
            return redirect(url_for('index'))
    return render_template('edit.html', form = tempPost, thepost = thepost)

# Delete reply
@app.route('/deleteR/<reply_id>', methods=['POST', 'DELETE'])
@login_required
def deleteR(reply_id):
    theReply = Reply.query.get(reply_id)
    post = theReply.post
    db.session.delete(theReply)
    flash('Post deleted.')
    db.session.commit()
    return redirect(url_for('comments', post_id = post))

#Edit reply
@app.route('/editR/<reply_id>', methods=['GET', 'POST'])
@login_required
def editR(reply_id):
    tempPost = ReplyForm()
    theReply = Reply.query.get(reply_id)
    post = theReply.post
    db.session.delete(theReply)
    if tempPost.validate_on_submit():
        if (tempPost.body.data is not None):
            newreply = Reply(body = tempPost.body.data, user_id = current_user.id, post = post)
            db.session.add(newreply)
            db.session.commit()
            #flash('Reply edited!')
            return redirect(url_for('comments', post_id = post))
    return render_template('edit.html', form = tempPost, thepost = theReply)