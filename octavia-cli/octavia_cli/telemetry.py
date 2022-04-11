#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os

import analytics
import click
import pkg_resources


class TelemetryClient:

    DEV_WRITE_KEY = "4rQEsg0yKxpBjgcYai7eODZysG0G3cWE"
    PROD_WRITE_KEY = "4rQEsg0yKxpBjgcYai7eODZysG0G3cWE"

    def __init__(self, send_data: bool = False) -> None:
        self.segment_client = analytics.Client(self.write_key, send=send_data)

    @property
    def write_key(self):
        if os.getenv("OCTAVIA_ENV") == "dev":
            return TelemetryClient.DEV_WRITE_KEY
        else:
            return TelemetryClient.PROD_WRITE_KEY

    def _create_command_name(self, ctx):
        has_parent = True
        commands_name = [ctx.info_name]
        while has_parent:
            if ctx.parent is not None:
                ctx = ctx.parent
                commands_name.insert(0, ctx.info_name)
            else:
                has_parent = False
        return " ".join(commands_name)

    def track_command(self, ctx: click.Context):
        workspace_id = ctx.obj["WORKSPACE_ID"]
        segment_context = {"app": {"name": "octavia-cli", "version": pkg_resources.require("octavia-cli")[0].version}}
        self.segment_client.identify(anonymous_id=workspace_id, context=segment_context)
        command_name = self._create_command_name(ctx)
        self.segment_client.track(anonymous_id=workspace_id, event=command_name, context=segment_context)
