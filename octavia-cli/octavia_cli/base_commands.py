#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import typing as t

import click

from .telemetry import TelemetryClient


class OctaviaCommand(click.Command):
    def invoke(self, ctx: click.Context) -> t.Any:
        telemetry_client = TelemetryClient(ctx.obj["TELEMETRY_IS_ENABLED"])
        telemetry_client.track_command(ctx)
        return super().invoke(ctx)
