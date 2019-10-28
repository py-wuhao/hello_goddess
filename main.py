import time

from hello import Hello
from send_email import SendEmail

email = SendEmail()


def send_email(msg):
    email.send('hello_goddess', msg, ['15392746632@qq.com'])


def main():
    hello = Hello(True, ['葛'])
    hello.inform(send_email)
    while True:
        hello.get_sport_rank()
        hello.add_friend()
        hello.get_friend()
        hello.save_to_mysql()
        time.sleep(3 * 60)


if __name__ == '__main__':
    main()
