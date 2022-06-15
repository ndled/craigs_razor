import smtplib
import ssl
import time
from scraper import Post


class EmailServer:
    def __init__(self, email_address:str, password:str, email_server: str = "smtp.gmail.com", port:str = 465) -> None:
        self.email_address = email_address
        self.password = password
        self.email_server = email_server
        self.port = port

    @staticmethod
    def generate_plain_text_body(post_list:list[Post]):
        body = ""
        for post in post_list:
            body = body + (f"{post.url}\t{post.price}\t{post.title}\t{post.posted_date}\t{post.location}\t{post.origin}\n\n")
        return body
        
    @staticmethod
    def format_plain_text_email(subject:str = "Default Subject", body: str = f"This is a default test message sent at {time.time()}") -> str:
        return f"""Subject: {subject}\n\n{body}"""

    def send_plain_text_email(self, message: str, receiver_email: str) -> None:
        with smtplib.SMTP_SSL(self.email_server, port = self.port, context = ssl.create_default_context()) as server:
            server.login(self.email_address, self.password)
            server.sendmail(self.email_address, receiver_email, message)


    # Need a send html email function tbh

