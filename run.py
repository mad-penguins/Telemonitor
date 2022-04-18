from time import sleep

import schedule

import bot as bot


def main():
    schedule.every(5).seconds.do(bot.write_to_base)
    schedule.every().day.at("23:59").do(bot.send_statistics_for_day)

    while True:
        schedule.run_pending()
        sleep(1)


if __name__ == '__main__':
    main()
