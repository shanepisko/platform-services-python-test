import json
import tornado.web

from pymongo import MongoClient
from tornado.gen import coroutine


class UserRewardsHandler(tornado.web.RequestHandler):

    @coroutine
    def get(self, email=None):
        print(email)
        client = MongoClient("mongodb", 27017)
        db = client["UserRewards"]
        if email:
            user_rewards = list(db.user_rewards.find({"email": email}, {"_id": 0}))
        else:
            user_rewards = list(db.user_rewards.find({}, {"_id": 0}))
        self.write(json.dumps(user_rewards))

    def post(self, updateEmail=None):
        """
            Recieve user order details
            should be a json object containing email, and order_total parameters
        """
        email = self.get_argument('email')
        order_total = round(float(self.get_argument('order_total')), 0)

        """
            Connect to MongoDB
        """
        client = MongoClient("mongodb", 27017)
        db = client["UserRewards"]

        """ Find related user object """
        user_rewards = list(db.user_rewards.find({"email": email}, {"_id": 0}).limit(1))
        user_rewards = user_rewards[0] if len(user_rewards) > 0 else None

        if not user_rewards:
                self.write("NO USER, need create %s %.0f" % (email, order_total))

                """ GET REWARD WHICH IS LESS THAN THE ORDER TOTAL sent with request """
                currRewards, nextRewards = self.get_tier_position(order_total)

                new_user = {
                    "email": email, # Email Address: the customer's email address (ex. "customer01@gmail.com")
                    "points": order_total, # Reward Points: the customer's rewards points (ex. 100)
                    "tier": currRewards['tier']  if currRewards else 'Not yet reached tier 1', # Rewards Tier: the rewards tier the customer has reached (ex. "A")
                    "rewardName": currRewards['rewardName']  if currRewards else 'Not yet reached tier 1', # Reward Tier Name: the name of the rewards tier (ex. "5% off purchase")
                    "nextTier": nextRewards['tier'], # Next Rewards Tier: the next rewards tier the customer can reach (ex. "B")
                    "nextRewardName": nextRewards['rewardName'], # Next Rewards Tier Name: the name of next rewards tier (ex. "10% off purchase")
                    "tierProgress": self.calc_progress(float(currRewards['points'] if currRewards else 0),float(nextRewards['points']),order_total)  # Next Rewards Tier Progress: the percentage the customer is away from reaching the next rewards tier (ex. 0.5)
                }
                # self.write(json.dumps(new_user))
                insert_res = db.user_rewards.insert_one(new_user)
                if insert_res:
                    self.write(json.dumps({"status":"success"}))
                else:
                    self.write(json.dumps({"status":"error", "message": "issue your request please review your submission and try again"}))
        else:
                # self.write(json.dumps(user_rewards))

                """ There is a user matching the post request, now need to add the new order total """
                updated_user_points = float(user_rewards['points']) + order_total
                """ GET REWARD WHICH IS LESS THAN THE ORDER TOTAL sent with request """
                currRewards, nextRewards = self.get_tier_position(updated_user_points)

                """
                    UPDATE the user with the new values
                    based on the query from get_tier_position
                    which returns the new current and next tiers
                """

                updated_user = {
                    "email": email, # Email Address: the customer's email address (ex. "customer01@gmail.com")
                    "points": updated_user_points, # Reward Points: the customer's rewards points (ex. 100)
                    "tier": currRewards['tier'] if currRewards else 'Not yet reached tier 1', # Rewards Tier: the rewards tier the customer has reached (ex. "A")
                    "rewardName": currRewards['rewardName'] if currRewards else 'Not yet reached tier 1', # Reward Tier Name: the name of the rewards tier (ex. "5% off purchase")
                    "nextTier": nextRewards['tier'] if nextRewards else 'Reached Reward Limit', # Next Rewards Tier: the next rewards tier the customer can reach (ex. "B")
                    "nextRewardName": nextRewards['rewardName'] if nextRewards else 'Reached Reward Limit', # Next Rewards Tier Name: the name of next rewards tier (ex. "10% off purchase")
                    "tierProgress": self.calc_progress(float(currRewards['points'] if currRewards else 0),float(nextRewards['points']),updated_user_points) if nextRewards else 'Reached Reward Limit' # Next Rewards Tier Progress: the percentage the customer is away from reaching the next rewards tier (ex. 0.5)
                }
                self.write(json.dumps(updated_user))

                newvalues = { "$set": updated_user }

                update_res = db.user_rewards.update_one(user_rewards, newvalues)
                # print(update_res)
                if update_res:
                    self.write(json.dumps({"status":"success"}))
                else:
                    self.write(json.dumps({"status":"error", "message": "issue with update please review your submission and try again"}))


    def calc_progress(self, curr_tier, next_tier, user_points):
        return (user_points - curr_tier) / (next_tier - curr_tier)

    def get_tier_position(self, order_total):
        client = MongoClient("mongodb", 27017)
        db = client["Rewards"]
        currRewards = list(db.rewards.find({'points':{'$lt':order_total}}, {'_id':0}).sort([('points', -1)]).limit(1))
        nextRewards = list(db.rewards.find({'points':{'$gt':order_total}}, {'_id':0}).sort([('points', 1)]).limit(1))
        return currRewards[0] if len(currRewards) > 0 else None, nextRewards[0] if len(nextRewards) > 0 else None
