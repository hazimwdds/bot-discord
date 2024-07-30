from .member import setup as setup_member
from .message import setup as setup_message

def setup(bot):
    setup_member(bot)
    setup_message(bot)
