#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
import typing as t

import click


class OctaviaCommand(click.Command):
    def make_context(
        self, info_name: t.Optional[str], args: t.List[str], parent: t.Optional[click.Context] = None, **extra: t.Any
    ) -> click.Context:
        try:
            return super().make_context(info_name, args, parent, **extra)
        except Exception as e:
            telemetry_client = parent.obj["TELEMETRY_CLIENT"]
            telemetry_client.track_command(parent, error=e, extra_info_name=info_name)
            raise e

    def invoke(self, ctx: click.Context) -> t.Any:
        telemetry_client = ctx.obj["TELEMETRY_CLIENT"]
        try:
            result = super().invoke(ctx)
        except Exception as e:
            telemetry_client.track_command(ctx, error=e)
            raise e
        telemetry_client.track_command(ctx)
        return result
