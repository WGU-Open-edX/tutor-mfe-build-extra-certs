import os
import shutil
from glob import glob
from pathlib import Path

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
for path in glob(str(importlib_resources.files("tutormfe_build_extra_certs") / "patches" / "*")):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item((os.path.basename(path), patch_file.read()))



#######################################
# CUSTOM CLI COMMANDS
#######################################

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
@click.option("--env-root", help="Tutor environment root path (auto-detected if not provided)")
@click.pass_obj
def set_cert(context, cert_path: str, env_root: str) -> None:
    """
    Copy a certificate file to the MFE build folder.

    CERT_PATH: Path to the certificate file to copy

    The certificate will be copied and renamed to 'vpn-cert.crt' in the MFE
    build folder so it can be used during the MFE build process.
    """
    # Get Tutor environment root if not provided
    if not env_root:
        try:
            # Try different methods to get the tutor root
            env_root = context.root
        except (AttributeError, TypeError):
            try:
                # Fallback: try to get from environment variable
                env_root = os.environ.get('TUTOR_ROOT')
                if not env_root:
                    # Final fallback: use default tutor root location
                    env_root = os.path.expanduser("~/.local/share/tutor")
            except:
                env_root = os.path.expanduser("~/.local/share/tutor")

    # Define the target directory - this is where MFE build happens
    mfe_build_dir = Path(env_root) / "env" / "plugins" / "mfe" / "build" / "mfe"

    # Ensure the build directory exists
    mfe_build_dir.mkdir(parents=True, exist_ok=True)

    # Define target certificate path
    target_cert_path = mfe_build_dir / "vpn-cert.crt"

    try:
        # Copy the certificate file
        shutil.copy2(cert_path, target_cert_path)
        click.echo(f"✅ Certificate copied successfully!")
        click.echo(f"   Source: {cert_path}")
        click.echo(f"   Target: {target_cert_path}")
        click.echo(f"")
        click.echo(f"The certificate will be automatically included in MFE builds.")

    except Exception as e:
        click.echo(f"❌ Error copying certificate: {e}", err=True)
        raise click.ClickException(f"Failed to copy certificate: {e}")


@mfe_build_extra_certs.command("remove-cert")
@click.option("--env-root", help="Tutor environment root path (auto-detected if not provided)")
@click.pass_obj
def remove_cert(context, env_root: str) -> None:
    """
    Remove the certificate from the MFE build folder.
    """
    # Get Tutor environment root if not provided
    if not env_root:
        try:
            # Try different methods to get the tutor root
            env_root = context.root
        except (AttributeError, TypeError):
            try:
                # Fallback: try to get from environment variable
                env_root = os.environ.get('TUTOR_ROOT')
                if not env_root:
                    # Final fallback: use default tutor root location
                    env_root = os.path.expanduser("~/.local/share/tutor")
            except:
                env_root = os.path.expanduser("~/.local/share/tutor")

    # Define the target certificate path
    mfe_build_dir = Path(env_root) / "env" / "plugins" / "mfe" / "build" / "mfe"
    target_cert_path = mfe_build_dir / "vpn-cert.crt"

    try:
        if target_cert_path.exists():
            target_cert_path.unlink()
            click.echo(f"✅ Certificate removed successfully!")
            click.echo(f"   Removed: {target_cert_path}")
        else:
            click.echo(f"ℹ️ No certificate found to remove at: {target_cert_path}")

    except Exception as e:
        click.echo(f"❌ Error removing certificate: {e}", err=True)
        raise click.ClickException(f"Failed to remove certificate: {e}")


@mfe_build_extra_certs.command("status")
@click.option("--env-root", help="Tutor environment root path (auto-detected if not provided)")
@click.pass_obj
def status(context, env_root: str) -> None:
    """
    Check the status of the certificate setup.
    """
    # Get Tutor environment root if not provided
    if not env_root:
        try:
            # Try different methods to get the tutor root
            env_root = context.root
        except (AttributeError, TypeError):
            try:
                # Fallback: try to get from environment variable
                env_root = os.environ.get('TUTOR_ROOT')
                if not env_root:
                    # Final fallback: use default tutor root location
                    env_root = os.path.expanduser("~/.local/share/tutor")
            except:
                env_root = os.path.expanduser("~/.local/share/tutor")

    # Define paths
    mfe_build_dir = Path(env_root) / "env" / "plugins" / "mfe" / "build" / "mfe"
    target_cert_path = mfe_build_dir / "vpn-cert.crt"

    click.echo(f"🔍 Certificate Status")
    click.echo(f"   Build directory: {mfe_build_dir}")
    click.echo(f"   Certificate path: {target_cert_path}")

    if target_cert_path.exists():
        # Get file info
        stat = target_cert_path.stat()
        click.echo(f"   Status: ✅ Certificate present")
        click.echo(f"   Size: {stat.st_size} bytes")
        click.echo(f"   Modified: {stat.st_mtime}")
    else:
        click.echo(f"   Status: ❌ No certificate found")
        click.echo(f"")
        click.echo(f"To add a certificate, run:")
        click.echo(f"   tutor mfe-build-extra-certs set-cert /path/to/your/certificate.crt")
