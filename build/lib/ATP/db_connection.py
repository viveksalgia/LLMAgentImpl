#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Oracle ATP connection file"""
###############################################################################
# Project - BroadieLLM
# Filename - db_connection.py
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

from dotenv import load_dotenv
import oracledb
import os


def create_atp_conn():

    load_dotenv()

    connection = oracledb.connect(
        config_dir=os.environ.get("ORA_ATP_CONFIG_DIR"),
        user=os.environ.get("ORA_DEV_ATP_USER"),
        password=os.environ.get("ORA_DEV_ATP_PASS"),
        dsn=os.environ.get("ORA_DEV_ATP_DSN"),
        wallet_location=os.environ.get("ORA_ATP_CONFIG_DIR"),
        wallet_password=os.environ.get("ORA_DEV_ATP_WALLET_PASS"),
    )

    return connection


if __name__ == "__main__":
    create_atp_conn()
