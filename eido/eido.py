import logging
import os
import jsonschema
import oyaml as yaml

import logmuse
from ubiquerg import VersionInHelpParser
from peppy import Project

from . import __version__
from .const import *

_LOGGER = logging.getLogger(__name__)


def build_argparser():
    banner = "%(prog)s - validate project metadata against a schema"
    additional_description = "\nhttps://github.com/pepkit/eido"

    parser = VersionInHelpParser(
            prog=PKG_NAME,
            description=banner,
            epilog=additional_description)

    parser.add_argument(
            "-V", "--version",
            action="version",
            version="%(prog)s {v}".format(v=__version__))

    parser.add_argument(
            "-p", "--pep", required=True,
            help="PEP configuration file in yaml format.")

    parser.add_argument(
            "-s", "--schema", required=True,
            help="PEP schema file in yaml format.")

    parser.add_argument(
            "-e", "--exclude-case", default=False, action="store_true",
            help="Whether to exclude the validation case from an error. "
                 "Only the human readable message explaining the error will be raised. "
                 "Useful when validating large PEPs.")
    return parser


def _preprocess_schema(schema_dict):
    """
    Preprocess schema before validation for user's convenience

    Preprocessing includes: renaming 'samples' to '_samples'
    since in the peppy.Project object _samples attribute holds the list of peppy.Samples objects.
    :param dict schema_dict: schema dictionary to preprocess
    :return dict: preprocessed schema
    """
    _LOGGER.debug("schema ori: {}".format(schema_dict))
    if "samples" in schema_dict["properties"]:
        schema_dict["properties"]["_samples"] = schema_dict["properties"]["samples"]
        del schema_dict["properties"]["samples"]
        schema_dict["required"][schema_dict["required"].index("samples")] = "_samples"
    _LOGGER.debug("schema edited: {}".format(schema_dict))
    return schema_dict


def _load_yaml(filepath):
    """
    Read a YAML file

    :param str filepath: path to the file to read
    :return dict: read data
    """
    with open(filepath, 'r') as f:
        data = yaml.safe_load(f)
    return data


def _read_schema(schema):
    if isinstance(schema, str) and os.path.isfile(schema):
        return _load_yaml(schema)
    elif isinstance(schema, dict):
        return schema
    raise TypeError("schema has to be either a dict or a path to an existing file")


def validate_project(project, schema, exclude_case=False):
    """
    Validate a project object against a schema

    :param peppy.Sample project: a project object to validate
    :param str | dict schema: schema dict to validate against or a path to one
    :param bool exclude_case: whether to exclude validated objects from the error.
        Useful when used ith large projects
    """
    schema_dict = _read_schema(schema=schema)
    project_dict = project.to_dict()
    _validate_object(project_dict, _preprocess_schema(schema_dict), exclude_case)


def _validate_object(object, schema, exclude_case=False):
    """
    Generic function to validate object against a schema

    :param Mapping object: an object to validate
    :param str | dict schema: schema dict to validate against or a path to one
    :param bool exclude_case: whether to exclude validated objects from the error.
        Useful when used ith large projects
    """
    try:
        jsonschema.validate(object, schema)
    except jsonschema.exceptions.ValidationError as e:
        if not exclude_case:
            raise e
        raise jsonschema.exceptions.ValidationError(e.message)


def validate_sample(project, sample_name, schema, exclude_case=False):
    """
    Validate the selected sample object against a schema

    :param peppy.Project project: a project object to validate
    :param str | int sample_name: name or index of the sample to validate
    :param str | dict schema: schema dict to validate against or a path to one
    :param bool exclude_case: whether to exclude validated objects from the error.
        Useful when used ith large projects
    :return:
    """
    schema_dict = _read_schema(schema=schema)
    sample_dict = project.samples[sample_name] if isinstance(sample_name, int) \
        else project.get_sample(sample_name)
    sample_schema_dict = schema_dict["properties"]["samples"]["items"]
    _validate_object(sample_dict, sample_schema_dict, exclude_case)


def main():
    """ Primary workflow """
    parser = logmuse.add_logging_options(build_argparser())
    args, remaining_args = parser.parse_known_args()
    logger_kwargs = {"level": args.verbosity, "devmode": args.logdev}
    logmuse.init_logger(name="peppy", **logger_kwargs)
    logmuse.init_logger(name=PKG_NAME, **logger_kwargs)
    global _LOGGER
    _LOGGER = logmuse.logger_via_cli(args)
    _LOGGER.debug("Creating a Project object from: {}".format(args.pep))
    p = Project(args.pep)
    _LOGGER.debug("Comparing the Project ('{}') against a schema: {}.".format(args.pep, args.schema))
    validate_project(p, args.schema, args.exclude_case)
