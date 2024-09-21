import schedule
import time
import subprocess

def job():
    subprocess.run(['python', 'scrape_menu.py'])
    subprocess.run(['python', 'notify_users.py'])

schedule.every().day.at("05:00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
