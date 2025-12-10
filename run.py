"""
Entry point for the SAT-Miner application.
"""
import click
from src.core.miner import SatMiner
from src.services.sentry_service import SentryService

@click.command()
@click.argument("url")
def main(url):
    """
Entry point for the SAT-Miner application.
"""
import click
import multiprocessing
from src.core.miner import SatMiner
from src.services.sentry_service import SentryService

@click.command()
@click.argument("url")
def main(url):
    """
    SAT-Miner: Zoom Link Aggregator
    
    Automated Zoom meeting link aggregator.
    
    Usage:
        python run.py "https://zoom.us/j/..."
    """
    # Initialize services
    SentryService.initialize()
    
    # Start Miner
    miner = SatMiner(url)
    miner.start()

if __name__ == "__main__":
    # Required for multiprocessing (GUI notifications)
    multiprocessing.freeze_support()
    main()
    # Initialize services
    SentryService.initialize()
    
    # Start Miner
    miner = SatMiner(url)
    miner.start()

if __name__ == "__main__":
    main()
