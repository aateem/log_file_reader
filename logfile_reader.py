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
        fileobj.seek(fileobj_size - buf_ind * 4096, 0)
    except IOError:
        fileobj.seek(0)

    return fileobj.readlines()


def is_considerable(log_entry, log_chunk, new_buff=True):
    '''
        Provides checking for line to be valid for writing to output
    '''
    matched = re.match(LOG_ENTRY_CHECK_PATTERN, log_entry)

    log_chunk_index = log_chunk.index(log_entry)

    # if start of the buffer (i.e. lines[0]) contains wrecked line
    # following code is supposed to find first line (starting from that wrecked)
    # that matches regexp for log entry
    if new_buff and not matched and log_chunk[log_chunk_index] != log_chunk[-1]:
        log_chunk_index += 1
        return is_considerable(log_chunk[log_chunk_index], log_chunk, False)
    elif not new_buff and not matched:
        return (False, [])

    # performing timedelta calculation (if one wants to change time unit by which difference is process)
    # should look here
    time_from_log_entry = time.strptime(matched.groups()[0], TIME_PARSE_PATTERN)
    current_time = time.localtime()

    timedelta = current_time.tm_min - time_from_log_entry.tm_min

    # performing slice for list with read lines from log file
    # so that it contains now pure, not broken lines
    log_chunk = log_chunk[log_chunk_index:]

    return (timedelta <= TIME_DELTA_LOG_ENTRY_FILTER, log_chunk)


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

            is_considerable_test, is_considerable_list = is_considerable(lines[0], lines)

            # we check here if we need read next buffer from log file
            if not is_considerable_test:
                buf_ind += 1
                lines = read_and_check(f, fsize, buf_ind)

                continue
            else:
                lines = is_considerable_list

            logging = False

            for line in lines:
                if is_considerable(line, lines, False)[0] and "INFO" not in line:
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
