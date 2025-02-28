import io
import os
from flask import Blueprint, make_response, request, send_file, send_from_directory
from backend.jwt_manager import admin_required
from backend.logger import logger
from backend.functions.database import (
    db_get_all_exercises,
    db_get_all_users,
    db_get_submissions_by_user_exercise,
)

import pdfkit
import tempfile
from weasyprint import HTML, CSS

from backend.conf.config import cfg

# TODO: Add pdfkit to requirements
# TODO: Add wkhtmltopdf to requirements
# TODO: Add weasyprint to requirements

results_api = Blueprint("results_api", __name__)


@results_api.route("/generate-pdf", methods=["POST", "GET"])
def generate_pdf():

    data = request.json
    html_content = data.get("html")

    pdf_filename = "example.pdf"
    html = HTML(string=html_content)
    # css = CSS(string='h1, h2, h3 { color: red }, @page { size: A4; margin: 1cm }', base_url="https://localhost/api//statics/hugo/instructor/css/styles.min.c72361e491ee4f34520fb30ea592e4350cff77edfa29c53f60bc7729b6dc7e48.css")
    html.write_pdf(f"{ cfg.pdf_path }/{ pdf_filename }")
    # html.write_pdf(f"{ cfg.pdf_path }/{ pdf_filename }", stylesheets=[CSS("/home/lreuter/cyberrange/learners/backend/statics/hugo/instructor/css/styles.min.c72361e491ee4f34520fb30ea592e4350cff77edfa29c53f60bc7729b6dc7e48.css")])

    return send_file(
            f"{cfg.pdf_path}/{pdf_filename}",
            as_attachment=True,
            mimetype="application/pdf",
            download_name="download.pdf"
        )

    # return make_response(send_from_directory(cfg.pdf_path, pdf_filename))



    # print(html_content)


    # print(pdf_file)
    
    # return send_file(
    #     io.BytesIO(pdf_file),
    #     as_attachment=True,
    #     mimetype="application/pdf",
    #     download_name="download.pdf"
    # )


@results_api.route("/md_results", methods=["GET"])
# @admin_required()
def getResults():

    results_md = ""
    import json

    for exercise in db_get_all_exercises():

        results_md += f"# {exercise.page_title}\n"
        results_md += f"## {exercise.exercise_name}\n"

        for user in db_get_all_users():
            _submissions = db_get_submissions_by_user_exercise(user.id, exercise.id)

            if _submissions and _submissions[0]:
                results_md += f"### { user.name }\n"

                submission_content = _submissions[0].form_data
                submission_content = json.loads(submission_content)

                for input_group, input_fields in submission_content.items():
                    if input_fields:
                        results_md += f"#### {input_group}\n"
                        results_md += "| Label | Content |\n"
                        results_md += "| ---- | ---- |\n"
                        for input_label, input_field in input_fields.items():
                            if "divider" in input_label:
                                results_md += f"| ---- | ---- |\n"
                            else:
                                if isinstance(input_field, str):
                                    input_field = input_field.replace("\n", "<br>")
                                results_md += f"| {input_label.replace('_', ' ')} | { input_field } |\n"

        results_md += "---\n"

    response = make_response(results_md)
    response.headers["Content-Disposition"] = "attachment; filename=sample.md"
    response.mimetype = "text/markdown"
    return response
