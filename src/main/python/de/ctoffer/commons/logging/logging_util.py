import functools
import inspect
import logging
import os.path


class FunctionLogger:
    def __init__(self):
        pass

    def __call__(self, *args, **kwargs):
        # capture entry args
        # capture error args
        # log entry
        # try execution
        # log error or log exit
        pass


def log_error(logger, re_raise=True, capture=frozenset()):
    def decorated(function):
        @functools.wraps(function)
        def wrapped(*args, **kwargs):
            captured_arguments = None
            if capture:
                bound_arguments = inspect.signature(function).bind(*args, **kwargs).arguments
                captured_arguments = dict()
                for key in capture:
                    captured_arguments[key] = bound_arguments.get(key, ValueError(f"No argument with name '{key}'"))

            try:
                return function(*args, **kwargs)
            except Exception as e:
                if logger:
                    element = get_last_traceback_element(e)

                    file_path = element.tb_frame.f_code.co_filename
                    if "python" in file_path:
                        module_path = file_path.split("python")[1]
                    elif "site-packages" in file_path:
                        module_path = file_path.split("site-packages")[1]
                    else:
                        module_path = file_path

                    module_path = os.path.normpath(module_path)
                    module_path, file_name = os.path.split(module_path)
                    module_path = ".".join(str(elem) for elem in module_path.split(os.path.sep) if elem)

                    if captured_arguments is None:
                        arguments = ""
                    else:
                        arguments = f" with captured {captured_arguments}"

                    location = f"{module_path} {file_name}: l. {element.tb_lineno}"
                    capture_function = f"{function.__name__}(){arguments}"
                    error = f"{type(e).__name__}: \"{e}\""

                    logger.error(f"{location} - {capture_function} - {error}")
                if re_raise:
                    raise

        return wrapped

    return decorated


def get_last_traceback_element(exception: Exception):
    trace_back = exception.__traceback__
    element = trace_back

    while element.tb_next is not None:
        element = element.tb_next

    return element


def log_entry(logger=logging.Logger, capture=frozenset(), level=logging.DEBUG):
    pass  # WIP


def log_exit(logger=logging.Logger, level=logging.DEBUG):
    pass  # WIP
