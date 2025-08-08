import random
from datetime import datetime, timedelta

def random_ip():
    return ".".join(str(random.randint(0, 255)) for _ in range(4))

def random_date():
    start = datetime.now() - timedelta(days=30)
    random_time = start + timedelta(seconds=random.randint(0, 30*24*60*60))
    return random_time.strftime("%d/%b/%Y:%H:%M:%S +0000")

def generate_log_line():
    ip = random_ip()
    date = random_date()
    method = random.choice(["GET", "POST", "PUT", "DELETE"])
    path = random.choice(["/index.html", "/login", "/dashboard", "/contact", "/logout"])
    status = random.choice([200, 302, 404, 500])
    size = random.randint(100, 5000)
    return f'{ip} - - [{date}] "{method} {path} HTTP/1.1" {status} {size}'

def generate_log_file(filename="lms-stage-access.log", num_lines=1000):
    with open(filename, "w") as f:
        for _ in range(num_lines):
            f.write(generate_log_line() + "\n")
    print(f"✅ Файл '{filename}' створено з {num_lines} логів.")

if __name__ == "__main__":
    generate_log_file()
