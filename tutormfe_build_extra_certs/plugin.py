import os
import shutil
import datetime
from glob import glob
from pathlib import Path
from typing import List, Tuple

import click
import importlib_resources
from tutor import config as tutor_config
from tutor import env
from tutor import hooks

from .__about__ import __version__

########################################
# CONFIGURATION
########################################

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        # Add your new settings that have default values here.
        # Each new setting is a pair: (setting_name, default_value).
        # Prefix your setting names with 'MFE_BUILD_EXTRA_CERTS_'.
        ("MFE_BUILD_EXTRA_CERTS_VERSION", __version__),
    ]
)


########################################
# TEMPLATE RENDERING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

hooks.Filters.ENV_TEMPLATE_ROOTS.add_items(
    # Root paths for template files, relative to the project root.
    [
        str(importlib_resources.files("tutormfe_build_extra_certs") / "templates"),
    ]
)

hooks.Filters.ENV_TEMPLATE_TARGETS.add_items(
    # For each pair (source_path, destination_path):
    # templates at ``source_path`` (relative to your ENV_TEMPLATE_ROOTS) will be
    # rendered to ``source_path/destination_path`` (relative to your Tutor environment).
    # For example, ``tutormfe_build_extra_certs/templates/mfe-build-extra-certs/build``
    # will be rendered to ``$(tutor config printroot)/env/plugins/mfe-build-extra-certs/build``.
    [
        ("mfe-build-extra-certs/build", "plugins"),
        ("mfe-build-extra-certs/apps", "plugins"),
    ],
)


########################################
# PATCH LOADING
# (It is safe & recommended to leave
#  this section as-is :)
########################################

# For each file in tutormfe_build_extra_certs/patches,
# apply a patch based on the file's name and contents.
for path in glob(
    str(importlib_resources.files("tutormfe_build_extra_certs") / "patches" / "*")
):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))


#######################################
# CUSTOM CLI COMMANDS
#######################################


def _get_env_root(context) -> str:
    """
    Get Tutor environment root path with fallback methods.
    """
    try:
        # Try different methods to get the tutor root
        return context.root
    except (AttributeError, TypeError):
        try:
            # Fallback: try to get from environment variable
            env_root = os.environ.get("TUTOR_ROOT")
            if env_root:
                return env_root
            # Final fallback: use default tutor root location
            return os.path.expanduser("~/.local/share/tutor")
        except:
            return os.path.expanduser("~/.local/share/tutor")


def _get_build_dirs(env_root: str) -> List[Tuple[str, Path]]:
    """
    Get list of build directories for certificate operations.
    Returns list of (build_type, build_dir) tuples.
    """
    mfe_build_dir = Path(env_root) / "env" / "plugins" / "mfe" / "build" / "mfe"
    openedx_build_dir = Path(env_root) / "env" / "build" / "openedx"
    return [("MFE", mfe_build_dir), ("OpenEDX", openedx_build_dir)]


# CLI command group for MFE build extra certificate management
@click.group()
def mfe_build_extra_certs() -> None:
    """
    Manage extra certificates for MFE builds in corporate environments.
    """
    pass


hooks.Filters.CLI_COMMANDS.add_item(mfe_build_extra_certs)


@mfe_build_extra_certs.command("set-cert")
@click.argument("cert_path", type=click.Path(exists=True, readable=True))
@click.option(
    "--env-root", help="Tutor environment root path (auto-detected if not provided)"
)
@click.pass_obj
def set_cert(context, cert_path: str, env_root: str) -> None:
    """
    Copy a certificate file to both MFE and OpenEDX build folders.

    CERT_PATH: Path to the certificate file to copy

    The certificate will be copied and renamed to 'vpn-cert.crt' in both the MFE
    build folder and the OpenEDX build folder so it can be used during build processes.
    """
    # Get Tutor environment root if not provided
    if not env_root:
        env_root = _get_env_root(context)

    build_dirs = _get_build_dirs(env_root)

    success_count = 0
    errors = []

    for build_type, build_dir in build_dirs:
        try:
            # Ensure the build directory exists
            build_dir.mkdir(parents=True, exist_ok=True)

            # Define target certificate path
            target_cert_path = build_dir / "vpn-cert.crt"

            # Copy the certificate file
            shutil.copy2(cert_path, target_cert_path)
            click.echo(f"✅ Certificate copied to {build_type} build folder!")
            click.echo(f"   Target: {target_cert_path}")
            success_count += 1

        except Exception as e:
            error_msg = f"Failed to copy certificate to {build_type} build folder: {e}"
            errors.append(error_msg)
            click.echo(f"❌ {error_msg}", err=True)

    if success_count > 0:
        click.echo(f"")
        click.echo(
            f"✅ Certificate copied to {success_count} build folder(s) successfully!"
        )
        click.echo(f"   Source: {cert_path}")
        click.echo(f"The certificate will be automatically included in builds.")

    if errors:
        if success_count == 0:
            raise click.ClickException(
                "Failed to copy certificate to any build folders"
            )
        else:
            click.echo(
                f"⚠️  Some operations failed, but certificate was copied to {success_count} folder(s)."
            )


@mfe_build_extra_certs.command("remove-cert")
@click.option(
    "--env-root", help="Tutor environment root path (auto-detected if not provided)"
)
@click.pass_obj
def remove_cert(context, env_root: str) -> None:
    """
    Remove the certificate from both MFE and OpenEDX build folders.
    """
    # Get Tutor environment root if not provided
    if not env_root:
        env_root = _get_env_root(context)

    build_dirs = _get_build_dirs(env_root)

    removed_count = 0
    not_found_count = 0
    errors = []

    for build_type, build_dir in build_dirs:
        target_cert_path = build_dir / "vpn-cert.crt"

        try:
            if target_cert_path.exists():
                target_cert_path.unlink()
                click.echo(f"✅ Certificate removed from {build_type} build folder!")
                click.echo(f"   Removed: {target_cert_path}")
                removed_count += 1
            else:
                click.echo(
                    f"ℹ️ No certificate found in {build_type} build folder: {target_cert_path}"
                )
                not_found_count += 1

        except Exception as e:
            error_msg = (
                f"Error removing certificate from {build_type} build folder: {e}"
            )
            errors.append(error_msg)
            click.echo(f"❌ {error_msg}", err=True)

    if removed_count > 0:
        click.echo(f"")
        click.echo(
            f"✅ Certificate removed from {removed_count} build folder(s) successfully!"
        )
    elif not_found_count == len(build_dirs):
        click.echo(f"")
        click.echo(f"ℹ️ No certificates found in any build folders.")

    if errors:
        if removed_count == 0:
            raise click.ClickException(
                "Failed to remove certificate from any build folders"
            )
        else:
            click.echo(
                f"⚠️  Some operations failed, but certificate was removed from {removed_count} folder(s)."
            )


@mfe_build_extra_certs.command("status")
@click.option(
    "--env-root", help="Tutor environment root path (auto-detected if not provided)"
)
@click.pass_obj
def status(context, env_root: str) -> None:
    """
    Check the status of the certificate setup in both MFE and OpenEDX build folders.
    """
    # Get Tutor environment root if not provided
    if not env_root:
        env_root = _get_env_root(context)

    build_dirs = _get_build_dirs(env_root)

    click.echo(f"🔍 Certificate Status")
    click.echo(f"   Environment root: {env_root}")
    click.echo(f"")

    any_cert_found = False

    for build_type, build_dir in build_dirs:
        target_cert_path = build_dir / "vpn-cert.crt"

        click.echo(f"📁 {build_type} Build:")
        click.echo(f"   Directory: {build_dir}")
        click.echo(f"   Certificate: {target_cert_path}")

        if target_cert_path.exists():
            # Get file info
            stat = target_cert_path.stat()
            modified_time = datetime.datetime.fromtimestamp(stat.st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            click.echo(f"   Status: ✅ Certificate present")
            click.echo(f"   Size: {stat.st_size} bytes")
            click.echo(f"   Modified: {modified_time}")
            any_cert_found = True
        else:
            click.echo(f"   Status: ❌ No certificate found")

        click.echo(f"")

    if not any_cert_found:
        click.echo(f"To add certificates, run:")
        click.echo(
            f"   tutor mfe-build-extra-certs set-cert /path/to/your/certificate.crt"
        )
