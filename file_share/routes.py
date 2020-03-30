import os
from dotenv import load_dotenv
from flask import render_template, redirect, request, Blueprint
from s3_functions import upload_file, download_file, list_files

load_dotenv()
bucket = os.getenv('BACK_END_BUCKET')

bp = Blueprint('routes', __name__, url_prefix='/')


@bp.route('/')
def home():
    """Home page rendering list of files with index.html file."""
    files = list_files(bucket)
    return render_template('index.html', contents=files)


@bp.route('/upload', methods=['POST'])
def upload():
    """Upload a file to the S3 bucket."""
    if request.method == 'POST':
        file = request.files['file']
        file.save(file.filename)
        upload_file(file.filename, bucket)
        try:
            os.remove(file.filename)
        except OSError:
            pass
        return redirect('/')


@bp.route('/download/<file_name>', methods=['GET'])
def download(file_name):
    """Download a file from the S3 bucket to the local downloads folder."""
    if request.method == 'GET':
        download_file(file_name, bucket)
