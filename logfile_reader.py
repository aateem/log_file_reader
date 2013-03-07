#!/usr/bin/python

import time
import re

LOG_ENTRY_CHECK_PATTERN = "PID\s\(\d+\):\s((\d{4})(\-(\d{2})){2}\s((\d{2})\:){2}(\d{2}))"
TIME_PARSE_PATTERN = "%Y-%m-%d %H:%M:%S"
TIME_DELTA_LOG_ENTRY_FILTER = 5
PATH_TO_LOG_FILE = ""


def read_and_check(fileobj, fileobj_size, buf_ind):
    # if we try to read beyond start of file, must set file cursor
    # to beginning of file
    try:
        fileobj.seek(max(fileobj_size - buf_ind * 1024, 0), 0)
    except IOError:
        fileobj.seek(0)

    return fileobj.readlines()


def time_delta(log_entry):
    matched = re.match(LOG_ENTRY_CHECK_PATTERN, log_entry)

    time_from_log_entry = time.strptime(matched.groups()[0], TIME_PARSE_PATTERN)
    current_time = time.localtime()

    timedelta = current_time.tm_min - time_from_log_entry.tm_min

    return timedelta <= TIME_DELTA_LOG_ENTRY_FILTER


def freader(path_to_file):
    # amount of read lines to be displayed
    chunk_lines = []

    with open(path_to_file, "r") as f:
        f.seek(0, 2)  # postion in file (set at end)
        fsize = f.tell()  # get size of file
        buf_ind = 1  # for maintaining count of buffers to read

        # time difference for log entry retrieving
        #past_time_edge = (datetime.datetime.now() + datetime.timedelta(minutes=-5)).strftime('%Y-%m-%d %H:%M:%S')

        lines = read_and_check(f, fsize, buf_ind)

        while True:
            if time_delta(lines[0]):
                buf_ind += 1
                lines = read_and_check(f, fsize, buf_ind)

                continue

            logging = False

            for line in lines:
                if time_delta(line):
                    logging = True
                    if logging and "INFO" not in line:
                        chunk_lines.append(line)

            break

    return chunk_lines
