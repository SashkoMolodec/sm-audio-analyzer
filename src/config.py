import os

class Config:
    """Configuration from environment variables"""

    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'redpanda:9091')
    KAFKA_CONSUMER_GROUP = os.getenv('KAFKA_CONSUMER_GROUP', 'audio-analyzer-group')

    # Topics
    ANALYZE_TRACK_TOPIC = 'analyze-track-tasks'
    ANALYSIS_COMPLETE_TOPIC = 'track-analysis-complete'

    # Paths
    ANALYSIS_RESULTS_PATH = os.getenv('ANALYSIS_RESULTS_PATH', '/Users/okravch/my/sm/analysis-results')

    # Analysis settings
    ANALYSIS_VERSION = os.getenv('ANALYSIS_VERSION', '1.0')
