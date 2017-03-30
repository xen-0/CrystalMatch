# Error codes for the Extended Focus Image Service

MISSING_JOB_ID_ERR = (101, "job_id entry not found in JSON content of received STOMP message body.")

JOB_ID_MISMATCH_ERR = (102, "job_id entry in STOMP JSON message body does not match entry in the message header.")

MISSING_FIELD_ERR = (103, "The STOMP JSON message body does not contain all required keys.")

INVALID_OUT_PATH_ERR = (104, "The output path is invalid or does not have a valid extension.")

INVALID_TARGET_DIR_ERR = (105, "Target directory cannot be reached")

HELICON_TIMEOUT_ERR = (106, "Helicon Focus took too long to complete or did not return a result. This may be due to "
                            "an interrupt message which requires user attention - please log into the server to "
                            "determine why this operation did not complete.")

HELICON_ERR = (107, "Helicon Focus returned an error response - please check log files on the server for the "
                    "error message.")

MALFORMED_JSON_ERR = (108, "Malformed JSON request in STOMP message body.")

EMPTY_TARGET_DIR_ERR = (109, "Target directory does not contain any valid files for stacking.")
