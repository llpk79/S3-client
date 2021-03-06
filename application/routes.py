import os
from datetime import datetime
from .database import db_session
from dotenv import load_dotenv
from flask import render_template, redirect, request, Blueprint, send_file, g
from .s3_functions import upload_file, download_file, get_file_list
from flask_security import login_required
from io import BytesIO
from .models import Files

load_dotenv()
bucket = os.getenv("BACK_END_BUCKET")

bp = Blueprint("routes", __name__)


@bp.route("/")
def home():
    return redirect("index")


@bp.route("/index", methods=["POST", "GET"])
@login_required
def index():
    """Index page renders index.html."""
    owned_files, shared_files = [], []
    # Get list of files from S3.
    all_files = get_file_list(bucket)
    if all_files and g.user:
        for file in all_files:
            # Get file metadata from Aurora.
            stored_files = Files.query.filter_by(name=file["Key"]).all()
            # Parse files into appropriate list.
            for stored_file in stored_files[-1:]:
                if stored_file and stored_file.owner_id == g.user.id:
                    owned_files.append(file)
                elif (
                    stored_file
                    and stored_file.shared
                    and stored_file.owner_id != g.user.id
                ):
                    shared_files.append(file)
    return render_template(
        "index.html", owned_files=owned_files, shared_files=shared_files
    )


@bp.route("/upload", methods=["POST"])
@login_required
def upload():
    """Upload a file to the S3 bucket."""
    if request.method == "POST":
        # Get file object from form.
        file = request.files["file"]
        if file.filename:
            file.save(file.filename)
            # Insert file metadata into Aurora
            db_file = Files(
                name=file.filename,
                upload_time=f"{datetime.now()}",
                shared=False,
                owner_id=g.user.id,
            )
            db_session.begin()
            db_session.add(db_file)
            db_session.commit()

            # Upload file contents to S3.
            upload_file(file.filename, bucket)
            # Remove local copy of file.
            try:
                os.remove(file.filename)
            except OSError:
                pass
        return redirect("index")


@bp.route("/download/<file_name>", methods=["GET", "POST"])
@login_required
def download(file_name):
    """Download a file from the S3 bucket to the local downloads folder."""
    if request.method == "GET":
        # Update file metadata in Aurora.
        file_record = Files.query.filter_by(name=file_name).all()[-1]
        db_session.begin()
        file_record.last_download = f"{datetime.now()}"
        db_session.commit()

        # Get file bytes from S3.
        output_bytes = download_file(file_name, bucket)
        # Create file object from bytes to pass to send_file.
        output_file = BytesIO(output_bytes)
        return send_file(
                filename_or_fp=output_file,
                as_attachment=True,
                attachment_filename=file_name,
        )


@bp.route("/share", methods=["POST"])
def share():
    """Share files with other users."""
    if request.method == "POST":
        # Get list of files user wishes to share from form.
        shared_files = request.form.getlist("share_files")
        for shared_file in shared_files:
            # Update metadata in Aurora to reflect shared status.
            file = Files.query.filter_by(name=shared_file).all()[-1]
            db_session.begin()
            file.shared = True
            db_session.commit()
        return redirect("index")
