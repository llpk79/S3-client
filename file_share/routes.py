import os
from dotenv import load_dotenv
from flask import render_template, redirect, request, Blueprint, send_file
from .s3_functions import upload_file, download_file, list_files
from flask_security import login_required

load_dotenv()
bucket = os.getenv('BACK_END_BUCKET')

bp = Blueprint('routes', __name__)


@bp.route('/')
# @login_user
def index():
    """Home page rendering list of files with index.html file."""
    files = list_files(bucket)
    return render_template('files/index.html', contents=files)


@bp.route('/upload', methods=['POST'])
@login_required
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
@login_required
def download(file_name):
    """Download a file from the S3 bucket to the local downloads folder."""
    if request.method == 'GET':
        output = download_file(file_name, bucket)
        return send_file(filename_or_fp=output, as_attachment=True)
