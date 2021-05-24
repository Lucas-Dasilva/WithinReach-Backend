import unittest
from app import app, db
from app.models import Post, Reply, User, reactedPost, reactedReply

# python3 -m unittest -v app/tests/test_models.py

class UserModelCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password(self):
        user = User(username = 'bernard')
        user.set_password('yes')
        self.assertFalse(user.get_password('no'))
        self.assertTrue(user.get_password('yes'))

    # Test Post table
    def test_post(self):
        # Adding 2 posts associated to u1
        p1 = Post(id = 1, body = 'testpost', likes = 3,
            latitude = '47.5', longitude = '-120.2', user_id = 10)
        p2 = Post(id = 2, body = 'testpost2', likes = 5,
            latitude = '52.5', longitude = '-130.7', user_id = 10)
        db.session.add(p1)
        db.session.add(p2)
        db.session.commit()
        # Adding 2 users, only u1 has posts
        u1 = User(id = 10, username = 'bernard', latitude = '47.5',
            longitude = '-120.2', karma = 100)
        u2 = User(id = 7, username = 'dolores', latitude = '52.5',
            longitude = '-130.7', karma = 100)
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()

        # Checking if p1,p2 are associated with u1
        self.assertEqual(u1.posts.count(), 2)
        # Checking that no posts are associated with u2
        self.assertEqual(u2.posts.count(), 0)

        # Checking values of p1
        self.assertEqual(u1.posts.first().id, 1)
        self.assertEqual(u1.posts.first().body, 'testpost')
        self.assertEqual(u1.posts.first().likes, 3)
        self.assertEqual(u1.posts.first().latitude, '47.5')
        self.assertEqual(u1.posts.first().longitude, '-120.2')
        self.assertEqual(u1.posts.first().user_id, 10)

        # Removing p1, check that is was removed
        db.session.delete(p1)
        db.session.commit()
        self.assertEqual(u1.posts.count(), 1)

        # Check that p2 is still associated with u1
        self.assertEqual(u1.posts.first().id, 2)


    # Test Reply table
    def test_reply(self):
        # Adding reply r1 associated with u1 and p1
        r1 = Reply(id = 1, body = 'testreply', likes = 2,
            post = 5, user_id = 11)
        db.session.add(r1)
        db.session.commit()
        u1 = User(id = 11, username = 'bernard', latitude = '47.5',
            longitude = '-120.2', karma = 100)
        db.session.add(u1)
        db.session.commit()
        p1 = Post(id = 5, body = 'testpost', likes = 3,
            latitude = '47.5', longitude = '-120.2', user_id = 11)
        db.session.add(p1)
        db.session.commit()

        # Check values of r1, and whether it is associated with u1,p1
        self.assertEqual(p1.replies.count(), 1)
        self.assertEqual(p1.replies.first().id, 1)
        self.assertEqual(p1.replies.first().body, 'testreply')
        self.assertEqual(p1.replies.first().likes, 2)
        self.assertEqual(p1.replies.first().post, 5)
        self.assertEqual(p1.replies.first().user_id, 11)

        # Remove r1, check that p1 contains no replies
        db.session.delete(r1)
        db.session.commit()
        self.assertEqual(p1.replies.count(), 0)
        

    # Test reactedPost table
    def test_reactedPost(self):
        # Adding reaction rp1, associating with p1,u1
        # Status set to none to begin test
        rp1 = reactedPost(id = 1, post = 1, status = 0, user_id = 11)
        # Adding reaction rp2, associating with p2,u1
        # Status = liked
        rp2 = reactedPost(id = 2, post = 2, status = 1, user_id = 11)
        # Adding reaction rp3, associating with p3,u1
        # Status = disliked
        rp3 = reactedPost(id = 3, post = 3, status = -1, user_id = 11)
        db.session.add(rp1)
        db.session.add(rp2)
        db.session.add(rp3)
        db.session.commit()
        u1 = User(id = 11, username = 'bernard', latitude = '47.5',
            longitude = '-120.2', karma = 100)
        db.session.add(u1)
        db.session.commit()
        p1 = Post(id = 1, body = 'testpost1', likes = 3,
            latitude = '47.5', longitude = '-120.2', user_id = 11)
        p2 = Post(id = 2, body = 'testpost2', likes = 2,
            latitude = '47.5', longitude = '-120.2', user_id = 11)
        p3 = Post(id = 3, body = 'testpost3', likes = 4,
            latitude = '47.5', longitude = '-120.2', user_id = 11)
        db.session.add(p1)
        db.session.add(p2)
        db.session.add(p3)
        db.session.commit()

        # Checking that rp1 is associated with p1,u1,
        # and whether status is none
        self.assertEqual(u1.reactions.first().id, 1)
        self.assertEqual(u1.reactions.first().post, 1)
        self.assertEqual(u1.reactions.first().status, 0)
        # Removing rp1
        db.session.delete(rp1)
        db.session.commit()

        # Checking that rp2 is associated with p2,u1,
        # and whether status is liked
        self.assertEqual(u1.reactions.first().id, 2)
        self.assertEqual(u1.reactions.first().post, 2)
        self.assertEqual(u1.reactions.first().status, 1)
        # Removing rp2
        db.session.delete(rp2)
        db.session.commit()

        # Checking that rp3 is associated with p3,u1,
        # and whether status is disliked
        self.assertEqual(u1.reactions.first().id, 3)
        self.assertEqual(u1.reactions.first().post, 3)
        self.assertEqual(u1.reactions.first().status, -1)

    # Test reactedReply table
    def test_reactedReply(self):
        # Adding reaction rp1, associating with r1,u1
        # Status set to none to begin test
        rp1 = reactedReply(id = 1, reply = 1, status = 0, user_id = 11)
        # Adding reaction rp2, associating with r2,u1
        # Status = liked
        rp2 = reactedReply(id = 2, reply = 2, status = 1, user_id = 11)
        # Adding reaction rp3, associating with r3,u1
        # Status = disliked
        rp3 = reactedReply(id = 3, reply = 3, status = -1, user_id = 11)
        db.session.add(rp1)
        db.session.add(rp2)
        db.session.add(rp3)
        db.session.commit()
        u1 = User(id = 11, username = 'bernard', latitude = '47.5',
            longitude = '-120.2', karma = 100)
        db.session.add(u1)
        db.session.commit()
        r1 = Reply(id = 1, body = 'testreply1', likes = 3, user_id = 11)
        r2 = Reply(id = 2, body = 'testreply2', likes = 2, user_id = 11)
        r3 = Reply(id = 3, body = 'testreply3', likes = 4, user_id = 11)
        db.session.add(r1)
        db.session.add(r2)
        db.session.add(r3)
        db.session.commit()

        # Checking that rp1 is associated with r1,u1,
        # and whether status is none
        self.assertEqual(u1.reactionsR.first().id, 1)
        self.assertEqual(u1.reactionsR.first().reply, 1)
        self.assertEqual(u1.reactionsR.first().status, 0)
        # Removing rp1
        db.session.delete(rp1)
        db.session.commit()

        # Checking that rp2 is associated with r2,u1,
        # and whether status is liked
        self.assertEqual(u1.reactionsR.first().id, 2)
        self.assertEqual(u1.reactionsR.first().reply, 2)
        self.assertEqual(u1.reactionsR.first().status, 1)
        # Removing rp2
        db.session.delete(rp2)
        db.session.commit()

        # Checking that rp3 is associated with r3,u1,
        # and whether status is disliked
        self.assertEqual(u1.reactionsR.first().id, 3)
        self.assertEqual(u1.reactionsR.first().reply, 3)
        self.assertEqual(u1.reactionsR.first().status, -1)


if __name__ == '__main__':
    unittest.main()
