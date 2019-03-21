import smtplib
import imaplib
from socket import gaierror
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def get_value(message: str, number=False) -> str or int:
    """Ввод пользовательских значений"""
    new_value = None
    if number:
        try:
            new_value = int(input(message))
        except ValueError:
            print('Введено недопустимое значение!')
    else:
        new_value = input(message)
    return new_value


class MailWorker:
    def __init__(self, message=None, **config):
        self.smtp_server = config['smtp_server'] if 'smtp_server' in config else ''
        self.smtp_port = config['smtp_port'] if 'smtp_port' in config else None
        self.imap_server = config['imap_server'] if 'imap_server' in config else ''
        self.imap_port = config['imap_port'] if 'imap_port' in config else None
        self.login = config['login'] if 'login' in config else ''
        self.password = config['password'] if 'password' in config else ''
        self.msg = message if isinstance(message, MIMEMultipart) else ''
        self.recipients = []

        self.configs = [
            self.smtp_server, self.smtp_port,
            self.imap_server, self.imap_port,
            self.login, self.password]

    def __change_config(self) -> None:
        """Изменить системные настройки"""
        print('Текущие настройки:')
        for idx, item in enumerate(self.configs):
            print(f'{idx + 1} - {item}')
        while True:
            user = input('\nВыберите 1-6. Выход - q:')
            if user == '1':
                self.smtp_server = get_value('Новое значение:')
            elif user == '2':
                self.smtp_port = get_value('Новое значение:', number=True)
            elif user == '3':
                self.imap_server = get_value('Новое значение:')
            elif user == '4':
                self.imap_port = get_value('Новое значение:', number=True)
            elif user == '5':
                self.login = get_value('Новое значение:')
            elif user == '6':
                self.password = get_value('Новое значение:')
            elif user.lower() == 'q':
                break
            else:
                continue

    def __create_message(self) -> None:
        """Создать почтовое сообщение"""
        self.msg = MIMEMultipart()
        self.msg['From'] = self.login
        subject = input('Тема почтового сообщения:')
        self.msg['Subject'] = subject if subject else 'Без темы'
        while True:
            recipient = input('Адрес получателя почтового сообщения:')
            self.recipients.append(recipient)
            add_another = input('Добавить еще адрес (y/n)?')
            if add_another.lower() == 'n':
                break
        self.msg['To'] = ', '.join(self.recipients)
        text = input('Введите текст сообщения:')
        self.msg.attach(MIMEText(text, 'plain'))

    def __receive_message(self) -> None:
        """Получить последнее сообщение"""
        try:

            server = imaplib.IMAP4_SSL(self.imap_server, self.imap_port)
            server.login(self.login, self.password)
            server.list()
            server.select('inbox')
            result, data = server.uid('search', None, "ALL")  # Выполняет поиск и возвращает UID писем.
            latest_email_uid = data[0].split()[-1]
            result, data = server.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = data[0][1]
            server.logout()
            message = email.message_from_bytes(raw_email)
            message.get_payload(decode=True)
            print(message)
        except gaierror:
            print('Неправильные настройки сервера IMAP')

    def __send_message(self) -> None:
        """Отправить сообщение"""
        try:
            if self.msg and self.recipients:
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
                server.login(self.login, self.password)
                server.sendmail(self.login, self.recipients, self.msg.as_string())
                server.quit()
            else:
                print('Нет писем для отправки!')
        except smtplib.SMTPServerDisconnected:
            print('Неправильные настройки сервера SMTP')

    def run(self):
        while True:
            print(
                """ Работа с электронной почтой
                1 - Получить почту
                2 - Отправить почту
                3 - Создать сообщение
                4 - Изменить настройки
                q - выйти из программы
                """)
            choice = input("Выберите нужное действие: ")
            if choice == '1':
                self.__receive_message()
            elif choice == '2':
                self.__send_message()
            elif choice == '3':
                self.__create_message()
            elif choice == '4':
                self.__change_config()
            elif choice.lower() == 'q':
                break


if __name__ == '__main__':
    z = MailWorker()
    z.run()
