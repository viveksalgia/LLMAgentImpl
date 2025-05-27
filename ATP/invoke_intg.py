#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Oracle ATP execution file"""
###############################################################################
# Project - BroadieLLM
# Filename - invoke_intg.py
# Arguments - None
# Created By - Vivek Salgia
# Creation Date - 04/29/2025
# Reviewed By -
# Reviewed Date -
# Change logs -
# Version   Date         Type   Changed By                  Comments
# =======   ============ ====   ==============  ===============================
# 1.0       29-Apr-2025   I     Vivek Salgia    Initial Creation
###############################################################################

from ATP.db_connection import create_atp_conn


def getdb_regdata(identifier: str, role: str):
    conn = create_atp_conn()
    payload = ""
    with conn.cursor() as cursor:
        cursor.execute(
            "SELECT submission_payload FROM INTG.OIC_INTG_SUBMISSION_DEFS WHERE UPPER(INTEGRATION_CODE) = UPPER(:intg_identifier) and UPPER(vbcs_role) = UPPER(:rolename)",
            intg_identifier=identifier,
            rolename=role,
        )

        payload = cursor.fetchone()[0]

    return payload


# This method invokes the OIC integration from ATP Database
# A pre-requisite to this is that integration should be registered in the database for submission
# for that user and role combination
# Input Parameters are
# - Integration Code
# - Username
# - Role
def invoke(identifier: str, role: str) -> str:
    """
    Use this function to submit Broad integrations. This is Broad specific only and will be used when user wants to submit an integration for Broad.
    This function accepts the integration code and role name (VBCS role name) and submits the integration.

    Args:
        identifier (str) : This is the integration code from the knowledge base
        role (str) : This is the VBCS Role from the knowledge base or user sent

    Returns:
        retmsg (str) : return message

    """

    conn = create_atp_conn()
    cursor = conn.cursor()

    retcode = cursor.var(int)
    retmsg = cursor.var(str)

    payload = getdb_regdata(identifier=identifier, role=role)

    # payload = (
    #     """{
    #     "IntegrationName": "BIT_I_317_SCIQ_SAP_REQU_INBO",
    #     "InstanceID": "TestOICInstanceId1",
    #     "RunDate": """
    #     + f'"{role}"'
    #     + """,
    #     "IntegrationVersion": "1.00.000",
    #     "SuccessNotification": [
    #         {
    #             "SuccessEmailTo": "vsalgia@broadinstitute.org",
    #             "SuccessFlag": "Y","""
    #     + f'"SuccessEmailSubject": "This is a test email for {identifier} "'
    #     + """,
    #             "SuccessAttachment": {
    #                 "Attachment": [
    #                     {"AttachmentFlag": "N", "FileReference": "", "FileName": ""}
    #                 ]
    #             }
    #         }
    #     ],
    #     "ErrorNotification": [
    #         {
    #             "ErrorEmailTo": "",
    #             "ScopeName": "",
    #             "ErrorFlag": "",
    #             "ErrorCode": "",
    #             "ErrorDescription": "",
    #             "ErrorMailSubject": "",
    #             "ErrorAttachment": {
    #                 "Attachment": [
    #                     {"AttachmentFlag": "", "FileReference": "", "FileName": ""}
    #                 ]
    #             }
    #         }
    #     ]
    # }"""
    # )

    cursor.callproc(
        "oic_utils_pkg.invoke_child_int",
        [
            retcode,
            retmsg,
            "AISubmittedJob",
            "erpintegrationuser",
            identifier.upper(),
            "VBCSRole",
            role,
            payload,
        ],
    )

    retfunc = lambda retmsg: (
        retmsg.values[0]
        if (retmsg.values[0] is not None)
        else "Integration submitted successfully"
    )
    return retfunc(retmsg)


if __name__ == "__main__":
    retmsg = invoke("I_329_KEYUSA_SAP_INBOUND", "Administrator")
    print(retmsg)
