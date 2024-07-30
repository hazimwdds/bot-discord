from .utility import setup as setup_utility
from .moderation import setup as setup_moderation
from .report_suggestion import setup_func as setup_report_suggestion
from .ticket import setup as setup_ticket

def setup(bot):
    setup_utility(bot)
    setup_moderation(bot)
    setup_report_suggestion(bot)
    setup_ticket(bot)
