import uuid
from datetime import datetime
from decimal import *

from flask import request
from flask import render_template
from werkzeug.utils import secure_filename

from services.aws import s3
from services.aws import ses

from models.transactions import Transactions

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = ['csv']

MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
          'August', 'September', 'October', 'November', 'December']

transactions = Transactions()


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def transoform(data):
    try:
        if data['transaction'][0] not in ["+", "-"]:
            return "Transaction needs a sign: \"+\" or \"-\"", 400
        elif data['transaction'][0] == "+":
            data['type'] = 'credit'
            data['transaction'] = Decimal(data['transaction'][1:])
        elif data['transaction'][0] == "-":
            data['type'] = 'debit'
            data['transaction'] = -Decimal(data['transaction'][1:])
        else:
            return "Transaction unknown", 400
        data['date'] = datetime.strptime(data['date'], '%Y/%m/%d').date()
        data['uid'] = uuid.uuid4()
        return data
    except Exception as e:
        raise e


def get():
    try:
        id = request.args.get('id')
        res = transactions.get_transactions(id)
        return res
    except Exception as e:
        return str(e), 400


def insert():
    try:
        data = request.json
        if type(data) is not list:
            data = [data]
        if len(data) > 0:
            data = [transoform(item) for item in data]
            res = transactions.insert_transactions(data)
        summary = process_summary()
        res = send_email(summary)
        return res
    except Exception as e:
        return str(e), 400


def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            return 'No file part', 400
        file = request.files['file']
        if file.filename == '':
            return 'No selected file', 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            s3.upload_fileobj(
                file,
                "stori-transactions-m3598",
                filename,
                ExtraArgs={
                    "ContentType": file.content_type
                }
            )
            return 'A lambda function will be triggered and you will receive an email with your summary', 200
    return render_template("index.html")


def process_summary():
    try:
        data = transactions.get_transactions()

        total_balance = 0.0

        count_month = {}

        count_credit_month = {}
        sum_credit_month = {}
        avg_credit_month = {}

        count_debit_month = {}
        sum_debit_month = {}
        avg_debit_month = {}

        for month in MONTHS:
            count_month[month] = 0
            count_credit_month[month] = 0
            sum_credit_month[month] = 0.0
            avg_credit_month[month] = 0.0
            count_debit_month[month] = 0
            sum_debit_month[month] = 0.0
            avg_debit_month[month] = 0.0

        debit_balance = 0.0
        debit_count = 0
        credit_balance = 0.0
        credit_count = 0

        for item in data:
            item['date'] = datetime.strptime(item['date'], '%Y-%m-%d').date()
            item['transaction'] = float(item['transaction'])
            current_month = MONTHS[item['date'].month-1]
            count_month[current_month] += 1
            total_balance += item['transaction']
            if item['type'] == "credit":
                credit_balance += item['transaction']
                credit_count += 1
                count_credit_month[current_month] += 1
                sum_credit_month[current_month] += item['transaction']
            else:
                debit_balance += item['transaction']
                debit_count += 1
                count_debit_month[current_month] += 1
                sum_debit_month[current_month] += item['transaction']

        for month in MONTHS:
            avg_credit_month[month] = sum_credit_month[month] / count_credit_month[month] if count_credit_month[month] > 0\
                else 0.0
            avg_debit_month[month] = sum_debit_month[month]/count_debit_month[month] if count_debit_month[month] > 0\
                else 0.0

        avg_debit = debit_balance / float(debit_count) if debit_count > 0 else 0
        avg_credit = credit_balance / float(credit_count) if credit_count > 0 else 0

        res = {
            'Total Balance:': total_balance,
            'Months Transactions:': count_month,
            'Months Credit Average:': avg_credit_month,
            'Months Debit Average:': avg_debit_month,
            'Average debit amount:': avg_debit,
            'Average credit amount:': avg_credit,
        }
        return res
    except Exception as e:
        print(e)
        raise e


def send_email(data):
    sender = "mijail.erv@gmail.com"
    recipient = "mijail.erv@gmail.com"
    subject = "Stori transactions summary"
    body_text = ("Stori transactions summary")
    body_html = render_template("email.html", data=data)
    charset = "UTF-8"
    try:
        response = ses.send_email(
            Destination={
                'ToAddresses': [
                    recipient,
                ],
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': body_html,
                    },
                    'Text': {
                        'Charset': charset,
                        'Data': body_text,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': subject,
                },
            },
            Source=sender
        )
    except Exception as e:
        return e, 400
    else:
        return f'Email sent: {response["MessageId"]}', 200
