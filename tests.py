import unittest
import os
from apps import app, db
from apps.models import User, Post
from datetime import datetime, timedelta
os.environ["DATABASE_URL"] = "sqlite://"



class UserModelCase(unittest.TestCase):

    def setUp(self):
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        print("Start test!")

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        print("Stop test!")


    def test_check_password(self):
        u = User(username="Mark")
        u.set_password("dog")
        self.assertTrue(u.check_password("dog"))
        self.assertFalse(u.check_password("Cat"))

    def test_avatar(self):
        u = User(username="Mark", email="mark@ukr.net")
        self.assertEqual(u.avatar(100), 'https://www.gravatar.com/avatar/e6cac309e9b898798cca2d70de75df9a?d=identicon&s=100')

    def test_follow(self):
        user_1 = User(username="Max", email="max@ukr.net")
        user_2 = User(username="Mark", email="mark@ukr.net")
        db.session.add(user_1)
        db.session.add(user_2)
        db.session.commit()

        self.assertEqual(user_1.follwed.all(), [])
        self.assertEqual(user_1.follwers.all(), [])

        user_1.follow(user_2)


        self.assertTrue(user_1.is_following(user_2))
        self.assertEqual(user_1.followed.count(), 1)
        self.assertEqual(user_1.followed.first().username, "Mark")
        self.assertEqual(user_2.followers.count().username, "Max")
        self.assertEqual(user_2.followers.count(), 1)

        db.session.commit()

        user_1.unfollow(user_2)
        db.session.commit()

        self.assertFalse(user_1.is_following(user_2))



    def test_followed_post(self):
        user_1 = User(username="Max", email="max@ukr.net")
        user_2 = User(username="Mark", email="mark@ukr.net")
        user_3 = User(username="Marat", email="marat@ukr.net")
        user_4 = User(username="David", email="david@ukr.net")
        db.session.add_all([user_1, user_2, user_3, user_4])

        now = datetime.utcnow()
        post_1 = Post(body="Max post", author=user_1, timestamp=now + timedelta(seconds=1))
        post_2 = Post(body="Mark post", author=user_1, timestamp=now + timedelta(seconds=1))
        post_3 = Post(body="Marat post", author=user_1, timestamp=now + timedelta(seconds=1))
        post_4 = Post(body="David post", author=user_1, timestamp=now + timedelta(seconds=1))
        db.session.add_all([post_1, post_2, post_3, post_4])

        db.session.commit()

        user_1.follow(user_2)
        user_1.follow(user_4)
        user_2.follow(user_3)
        user_3.follow(user_4)

        db.session.commit()

        f_1 = user_1.followed_post().all()
        f_2 = user_2.followed_post().all()
        f_3 = user_3.followed_post().all()
        f_4 = user_4.followed_post().all()

        self.assertEqual(f_4, [post_4])
        self.assertEqual(f_3, [post_4])
        self.assertEqual(f_2, [post_3])
        self.assertEqual(f_1, [post_4, post_2])



if __name__ == '__main__':
    unittest.main(verbosity=2)


# class TestString(unittest.TestCase):
#
#     def setUp(self):
#         print("Open file for a work")
#
#     def tearDown(self):
#         print("Close file for a work")
#
#     def test_upper(self):
#         self.assertEqual('food'.upper(), 'FOOD')
#         self.assertTrue("FOOD" == "FOOD")
#
#     def test_sum(self):
#         self.assertEqual(sum([1, 2, 3]), 6, "Should be 6")
# from prog_ssum import my_sum

    # def test_my_sum(self):
    #     self.assertEqual(my_sum(5, 10), 15, "Should be 15")