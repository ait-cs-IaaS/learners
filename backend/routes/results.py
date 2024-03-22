from flask import Blueprint, make_response
from backend.jwt_manager import admin_required
from backend.logger import logger
from backend.functions.database import (
    db_get_all_exercises,
    db_get_all_users,
    db_get_submissions_by_user_exercise,
)

results_api = Blueprint("results_api", __name__)


@results_api.route("/md_results", methods=["GET"])
@admin_required()
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
