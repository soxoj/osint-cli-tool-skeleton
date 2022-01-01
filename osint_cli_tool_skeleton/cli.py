"""
Commandline interface
"""
import asyncio
import logging
import platform

from argparse import ArgumentParser, RawDescriptionHelpFormatter

from .core import *


def setup_arguments_parser():
    from aiohttp import __version__ as aiohttp_version
    from ._version import __version__

    version_string = '\n'.join(
        [
            f'%(prog)s {__version__}',
            f'Python:  {platform.python_version()}',
            f'Aiohttp:  {aiohttp_version}',
        ]
    )

    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        description=f"OSINT tool v{__version__}\n"
    )
    parser.add_argument(
        "target",
        nargs='*',
        metavar="TARGET",
        help="One or more target to get info by.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=version_string,
        help="Display version information and dependencies.",
    )
    parser.add_argument(
        "--timeout",
        action="store",
        metavar='TIMEOUT',
        dest="timeout",
        default=100,
        help="Time in seconds to wait for execution",
    )
    parser.add_argument(
        "--cookie-jar-file",
        metavar="COOKIE_FILE",
        dest="cookie_file",
        default='',
        help="File with cookies.",
    )
    parser.add_argument(
        "--proxy",
        "-p",
        metavar='PROXY_URL',
        action="store",
        dest="proxy",
        default='',
        help="Make requests over a proxy. e.g. socks5://127.0.0.1:1080",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        dest="verbose",
        default=False,
        help="Display extra information and metrics.",
    )
    parser.add_argument(
        "--info",
        "-vv",
        action="store_true",
        dest="info",
        default=False,
        help="Display extra/service information and metrics.",
    )
    parser.add_argument(
        "--debug",
        "-vvv",
        "-d",
        action="store_true",
        dest="debug",
        default=False,
        help="Display extra/service/debug information and metrics, save responses in debug.log.",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        dest="no_color",
        default=False,
        help="Don't color terminal output",
    )
    parser.add_argument(
        "--no-progressbar",
        action="store_true",
        dest="no_progressbar",
        default=False,
        help="Don't show progressbar.",
    )

    return parser


async def main():
    # Logging
    log_level = logging.ERROR
    logging.basicConfig(
        format='[%(filename)s:%(lineno)d] %(levelname)-3s  %(asctime)s %(message)s',
        datefmt='%H:%M:%S',
        level=log_level,
    )
    logger = logging.getLogger('osint-cli-tool-skeleton')
    logger.setLevel(log_level)

    arg_parser = setup_arguments_parser()
    args = arg_parser.parse_args()

    if args.debug:
        log_level = logging.DEBUG
    elif args.info:
        log_level = logging.INFO
    elif args.verbose:
        log_level = logging.WARNING

    logger.setLevel(log_level)

    print(args)

    input_data = InputData('test')

    print(process([input_data]))


def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())


if __name__ == "__main__":
    run()