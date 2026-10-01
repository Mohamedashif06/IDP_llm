CYCLE_TEST_COLUMNS = [
    "s_no",
    "registration_no",
    "roll_no",
    "name",
    "q1",
    "q2",
    "q3",
    "q4",
    "q5",
    "6_a_i",
    "6_a_ii",
    "6_b_i",
    "6_b_ii",
    "7_a_i",
    "7_a_ii",
    "7_b_i",
    "7_b_ii",
    "8_a_i",
    "8_a_ii",
    "8_b_i",
    "8_b_ii",
    "total_50",
    "total_100",
]


def empty_record():
    return {column: "" for column in CYCLE_TEST_COLUMNS}


def normalize_record(record):
    result = empty_record()

    for key in result:
        if key in record:
            value = record[key]

            if value is None:
                value = ""

            result[key] = str(value).strip()

    return result