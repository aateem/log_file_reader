#!/usr/bin/python

import time
import re
import datetime

LOG_ENTRY_CHECK_PATTERN = "PID\s\(\d+\):\s((\d{4})(\-(\d{2})){2}\s((\d{2})\:){2}(\d{2}))"
TIME_PARSE_PATTERN = "%Y-%m-%d %H:%M:%S"
PATH_TO_LOG_FILE = ""
TIME_BORDER = time.mktime((datetime.datetime.now() - datetime.timedelta(minutes=5)).timetuple())


def time_check(matched_buff_entry):
    '''
        Compares time in form of unix time
    '''
    time_in_string = matched_buff_entry.groups()[0]
    time_structure = time.strptime(time_in_string, TIME_PARSE_PATTERN)
    log_entry_unix_time = time.mktime(time_structure)

    return log_entry_unix_time >= TIME_BORDER


def read_and_check(fileobj, fileobj_size, buf_ind):
    # if we try to read beyond start of file, must set file cursor
    # to beginning of file
    try:
        fileobj.seek(fileobj_size - buf_ind * 4096, 0)
    except IOError:
        fileobj.seek(0)

    return fileobj.readlines()


def is_considerable_inside_buff(log_entry):
    '''
        Provides checking for line to be valid for writing to output
    '''
    matched = re.match(LOG_ENTRY_CHECK_PATTERN, log_entry)

    if not matched:
        return False

    return time_check(matched)


def is_considerable_buff_edge(log_entry, log_chunk):
    matched = re.match(LOG_ENTRY_CHECK_PATTERN, log_entry)

    log_chunk_index = log_chunk.index(log_entry)

    if log_chunk[log_chunk_index] == log_chunk[-1]:
        return []

    if not matched:
        log_chunk_index += 1
        return is_considerable_buff_edge(log_chunk[log_chunk_index], log_chunk)

    if time_check(matched):
        return log_chunk[log_chunk_index:]

    return []


def freader(path_to_file, error_displaying=False):
    # amount of read lines to be displayed
    chunk_lines = []

    with open(path_to_file, "r") as f:
        f.seek(0, 2)  # postion in file (set at end)
        fsize = f.tell()  # get size of file
        buf_ind = 1  # for maintaining count of buffers to read

        lines = read_and_check(f, fsize, buf_ind)

        if not error_displaying:
            chunk_lines = is_considerable_buff_edge(lines[0], lines)
            return chunk_lines

        while True:

            buff_content = is_considerable_buff_edge(lines[0], lines)
            # we check here if we need read next buffer from log file
            if not buff_content:
                buf_ind += 1
                lines = read_and_check(f, fsize, buf_ind)

                continue

            lines = buff_content

            logging = False

            for line in lines:
                if is_considerable_inside_buff(line) and "INFO" not in line:
                    logging = True

                if "INFO" in line:
                    logging = False

                if logging:
                    chunk_lines.append(line.strip())

            break

    return chunk_lines

if __name__ == "__main__":
    for line in freader(PATH_TO_LOG_FILE):
        print line
