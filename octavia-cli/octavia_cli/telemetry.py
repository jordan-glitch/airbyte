#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import os
import uuid
from typing import Optional

import analytics
import click


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

    def _create_command_name(self, ctx, extra_info_name: Optional[str] = None):
        has_parent = True
        commands_name = [ctx.info_name]
        while has_parent:
            if ctx.parent is not None:
                ctx = ctx.parent
                commands_name.insert(0, ctx.info_name)
            else:
                has_parent = False
        if extra_info_name is not None:
            commands_name.append(extra_info_name)
        return " ".join(commands_name)

    def track_command(self, ctx: click.Context, error: Exception = None, extra_info_name: Optional[str] = None):
        user_id = ctx.obj.get("WORKSPACE_ID")
        anonymous_id = None if user_id else str(uuid.uuid1())

        segment_context = {"app": {"name": "octavia-cli", "version": ctx.obj.get("OCTAVIA_VERSION")}}
        segment_properties = {
            "success": error is None,
            "error_type": error.__class__.__name__,
            "project_is_initialized": ctx.obj.get("PROJECT_IS_INITIALIZED"),
        }
        self.segment_client.identify(user_id=user_id, anonymous_id=anonymous_id, context=segment_context)
        command_name = self._create_command_name(ctx, extra_info_name)
        self.segment_client.track(
            user_id=user_id, anonymous_id=anonymous_id, event=command_name, properties=segment_properties, context=segment_context
        )
