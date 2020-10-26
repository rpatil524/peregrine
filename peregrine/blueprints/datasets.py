import flask
import os
import re
from collections import OrderedDict

from peregrine.resources.submission import (
    graphql,
    set_read_access_projects_for_public_endpoint,
    set_read_access_projects,
)

from cdiserrors import UserError
from dictionaryutils import dictionary

blueprint = flask.Blueprint("datasets", "datasets")


@blueprint.route("/", methods=["GET"])
def get_datasets():
    """
    Get dataset level summary counts, if a deployment is configured
    to set PUBLIC_DATASETS to True, this endpoint will be open to
    anonymous users
    """
    nodes = flask.request.args.get("nodes", "")
    nodes = nodes.split(",")
    if not nodes:
        raise UserError("Need to provide target nodes in query param")
    if os.environ.get("PUBLIC_DATASETS", "false").lower() == "true":
        set_read_access_projects_for_public_endpoint()
    else:
        set_read_access_projects()
    projects = flask.g.read_access_projects
    if not projects:
        return flask.jsonify({})
    # construct a query that get counts for all projects
    # because graphql can't add structure to group by projects,
    # we labeled the count by project index and later parse it
    # with regex to add structure to response
    # OrderedDict([('i0_submitted_aligned_reads', 1), ('i1_submitted_aligned_reads', 1)])
    # OrderedDict([('i0_submitted_aligned_reads', 1), ('i1_submitted_aligned_reads', 1)])
    # {i0_submitted_aligned_reads: _submitted_aligned_reads_count(project_id: "DEV-DEV") }
    ##### working query is {i0_submitted_aligned_reads: _submitted_aligned_reads_count(project_id: "DEV-DEV") i1_submitted_aligned_reads: _submitted_aligned_reads_count(project_id: "QA-QA") }
    # run a query per project

    data = OrderedDict()
    for i, project_id in enumerate(projects):
        query = "{"
        query += (
            " ".join(
                map(
                    lambda x: """i{i}_{node}: _{node}_count(project_id: "{p}")""".format(
                        i=i, node=x, p=project_id
                    ),
                    nodes,
                )
            )
            + " "
        )
        query += "}"
        print("Cheking da query")
        print(query)
        data1, errors = graphql.execute_query(query, variables={})
        data.update(data1)
        if errors:
            return flask.jsonify({"data": data, "errors": errors}), 400
    result = {project_id: {} for project_id in projects}
    print(data)
    for name, value in data.items():
        match = re.search("^i(\d+)_(.*)", name)
        index = int(match.group(1))
        node = match.group(2)
        result[projects[index]][node] = value
    return flask.jsonify(result)


@blueprint.route("/projects", methods=["GET"])
def get_projects():
    """
    Get all projects high level information, if a deployment is configured
    to set PUBLIC_DATASETS to True, this endpoint will be open to
    anonymous users
    """
    if os.environ.get("PUBLIC_DATASETS", "false").lower() == "true":
        set_read_access_projects_for_public_endpoint()
    else:
        set_read_access_projects()
    projects = flask.g.read_access_projects
    if not projects:
        return flask.jsonify({"projects": []})
    # construct a query that get counts for all projects
    # because graphql can't add structure to group by projects,
    # we labeled the count by project index and later parse it
    # with regex to add structure to response
    query = "{project (first: 0) { name code dbgap_accession_number "
    for field in ["description", "image_url"]:
        if dictionary.schema["project"]["properties"].get(field):
            query += field + " "

    query += "}}"
    data, errors = graphql.execute_query(query, variables={})
    if errors:
        return flask.jsonify({"data": data, "errors": errors}), 400
    return flask.jsonify({"projects": data["project"]})
