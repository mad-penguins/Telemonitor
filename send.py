from sys import argv

import bot as bot

from Penger.penger import Penger
import settings


def main():
    if argv[1] == '--ssh':
        bot.notify_about_new_ssh_connection()
    else:
        p = Penger(settings.token)
        p.sendMessage(settings.chat_id, argv[1], disable_notification=True)


if __name__ == '__main__':
    main()
