from apscheduler.schedulers.background import BackgroundScheduler
from .models import UserStatistics


def month_cronjob():
    UserStatistics.objects.all().update(total_month_views=0)

def day_cronjob():
    UserStatistics.objects.all().update(total_today_views=0)


scheduler = BackgroundScheduler()
scheduler.add_job(month_cronjob, 'cron', day='1')
scheduler.add_job(day_cronjob, 'cron', hour=0)

