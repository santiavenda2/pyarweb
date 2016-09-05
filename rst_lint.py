import codecs
import collections
import os
import restructuredtext_lint
import sys

## Misc functions
## tomado de http://stackoverflow.com/questions/898669/how-can-i-detect-if-a-file-is-binary-non-text-in-python
ERROR_LEVEL = 'ERROR'
SEVERE_LEVEL = 'SEVERE'
WARNING_LEVEL = 'WARNING'
INFO_LEVEL = 'INFO'

textchars = bytearray([7, 8, 9, 10, 12, 13, 27]) + bytearray(range(0x20, 0x100))
is_binary_string = lambda bytes: bool(bytes.translate(None, textchars))

CANNOT_OPEN_FILE = 'CANNOT_OPEN_FILE'
DEFAULT_IGNORED_DIRS = {'.git'}
RST_EXTENSION = '.rst'
ERROR_LEVELS = [CANNOT_OPEN_FILE, SEVERE_LEVEL, ERROR_LEVEL, WARNING_LEVEL, INFO_LEVEL]

HEADER_MSG = """
Reporte de errores
==================

- Cannot open file: {}
- SEVERE: {}
- ERROR: {}
- WARNING: {}
- INFO: {}

"""

def get_folder_rst_errors(root_dir, ignored_dirs):
    errors_dict = collections.defaultdict(list)
    for r, dirs, files in os.walk(root_dir, topdown=True):
        [dirs.remove(d) for d in dirs if d in ignored_dirs]
        for f in files:
            # TODO: extraer a un metodo
            current_filename, current_file_extension = os.path.splitext(f)
            if current_file_extension == RST_EXTENSION:
                current_filepath = os.path.join(r, f)
                current_file = open(current_filepath, 'rb').read()    # TODO: hacerlo con with
                slug = current_filepath.replace(current_file_extension, '').replace(root_dir, '', 1)
                if len(current_file) > 0:
                    if is_binary_string(current_file):
                        # :-(
                        errors_dict[CANNOT_OPEN_FILE].append(slug)
                    else:
                        file_contents = current_file.decode('utf-8')
                        result = restructuredtext_lint.lint(file_contents)
                        for detail in result:
                            # detail_fixed = detail.message if not detail.message.startswith(
                            #     'Substitution def') else 'Substitution definition --trimmed-- missing contents'

                            # cur_detail = u'`{0} <{0}>`_ (line: {1}) - ``{2}``'.format(slug, detail.line, detail_fixed)
                            cur_detail = u'`{0} <{0}>`_ (line: {1}) - ``{2}``'.format(slug, detail.line, detail.message.replace('\n', ''))
                            errors_dict[detail.type].append(cur_detail)

    return errors_dict


def get_page_errors(root_dir, file, errors_dict):
    pass


def print_section(handle, severity, err_list, folder):
    section_title = 'Severidad: {}\n'.format(severity)
    handle.write(section_title)
    handle.write("{}\n".format('-' * (len(section_title)-1)))
    for item in err_list:
        handle.write(" - {} \n".format(item))
    handle.write('\n')


def write_report(errors_dict, folder, report_name='report.rst'):
    report_file_path = os.path.join(folder, report_name)
    with codecs.open(report_file_path, 'w', encoding='utf-8') as report_file:
        header = HEADER_MSG.format(len(errors_dict[CANNOT_OPEN_FILE]),
                                   len(errors_dict[SEVERE_LEVEL]),
                                   len(errors_dict[ERROR_LEVEL]),
                                   len(errors_dict[WARNING_LEVEL]),
                                   len(errors_dict[INFO_LEVEL]))
        report_file.write(header)
        for cur_level in ERROR_LEVELS:
            print_section(report_file, cur_level, errors_dict[cur_level], folder)


def main():
    if len(sys.argv) == 1:
        print('Se debe especificar el directorio donde se encuentra el clone del repo')
        sys.exit(1)

    folder = sys.argv[1]

    errors_dict = get_folder_rst_errors(folder, ignored_dirs=DEFAULT_IGNORED_DIRS)
    write_report(errors_dict, folder)


if __name__ == "__main__":
    main()