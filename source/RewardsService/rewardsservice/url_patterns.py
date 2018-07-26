from handlers.rewards_handler import RewardsHandler
from handlers.user_handler import UserRewardsHandler

url_patterns = [
    (r'/rewards', RewardsHandler),
    (r'/user-rewards', UserRewardsHandler),
]
