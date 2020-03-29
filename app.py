import os
from dotenv import load_dotenv
from flask import Flask, render_template, redirect, request, send_file
from s3_functions import upload_file, download_file, list_files

load_dotenv()
bucket = os.getenv('BACK_END_BUCKET')
app = Flask(__name__)


@app.route('/')
def home():
    """Home page rendering list of files with index.html file."""
    files = list_files(bucket)
    return render_template('index.html', contents=files)


@app.route('/upload', methods=['POST'])
def upload():
    """Upload a file to the S3 bucket."""
    if request.method == 'POST':
        file = request.files['file']
        file.save(file.filename)
        upload_file(file.filename, bucket)
        return redirect('/')


@app.route('/download/<file_name>', methods=['GET'])
def download(file_name):
    """Download a file from the S3 bucket to the local downloads folder."""
    if request.method == 'GET':
        output = download_file(file_name, bucket)
        return send_file(filename_or_fp=output, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
