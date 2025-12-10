import click
import multiprocessing
from src.core.miner import SatMiner
from src.services.sentry_service import SentryService
from src.version import __version__

"""
Entry point for the SAT-Miner application.
"""
@click.command()
@click.argument("url")
@click.version_option(__version__)
def main(url):
    """
    SAT-Miner: Zoom Link Aggregator
    
    Automated Zoom meeting link aggregator.
    
    Usage:
        python run.py "https://zoom.us/j/..."
    """
    # Initialize services
    SentryService.initialize()
    
    print(f"[*] SAT-Miner v{__version__}")
    
    # Start Miner
    miner = SatMiner(url)
    miner.start()

if __name__ == "__main__":
    # Required for multiprocessing (GUI notifications)
    multiprocessing.freeze_support()
    main()