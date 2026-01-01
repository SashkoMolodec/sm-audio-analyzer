#!/usr/bin/env python3
import logging
import sys
from pathlib import Path

# Add parent directory to path to import essentia module
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from essentia.analyzer import EssentiaAnalyzer
from essentia.json_writer import JsonWriter
from kafka_consumer import AnalysisTaskConsumer
from kafka_producer import AnalysisCompleteProducer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class AnalysisService:
    """Main service coordinating analysis tasks"""

    def __init__(self):
        self.config = Config()
        self.analyzer = EssentiaAnalyzer()
        self.json_writer = JsonWriter(self.config.ANALYSIS_RESULTS_PATH)
        self.result_producer = AnalysisCompleteProducer(self.config)
        self.consumer = AnalysisTaskConsumer(self.config, self.handle_task)

        logger.info("Audio Analysis Service initialized")
        logger.info(f"Results path: {self.config.ANALYSIS_RESULTS_PATH}")
        logger.info(f"Kafka servers: {self.config.KAFKA_BOOTSTRAP_SERVERS}")

    def handle_task(self, task: dict):
        """Process a single analysis task"""
        track_id = task.get('trackId')
        local_path = task.get('localPath')

        logger.info(f"Processing trackId={track_id}, path={local_path}")

        # Validate path
        audio_path = Path(local_path)
        if not audio_path.exists():
            error_msg = f"File not found: {local_path}"
            logger.error(error_msg)

            # Write error result to JSON
            json_path = self.json_writer.write_result(track_id, {}, success=False, error_message=error_msg)
            self.result_producer.send_complete(track_id, json_path, False, error_msg)
            return

        # Analyze
        try:
            features = self.analyzer.analyze_track(str(audio_path))

            # Write results to JSON
            json_path = self.json_writer.write_result(track_id, features, success=True)

            # Send completion message with JSON path
            self.result_producer.send_complete(track_id, json_path, True)

            logger.info(f"Successfully analyzed trackId={track_id}")

        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            logger.error(f"Error analyzing trackId={track_id}: {error_msg}", exc_info=True)

            # Write error result to JSON
            json_path = self.json_writer.write_result(track_id, {}, success=False, error_message=error_msg)
            self.result_producer.send_complete(track_id, json_path, False, error_msg)

    def run(self):
        """Start the service"""
        logger.info("Starting Audio Analysis Service...")
        try:
            self.consumer.start()
        except Exception as e:
            logger.error(f"Service error: {e}", exc_info=True)
        finally:
            self.result_producer.close()
            logger.info("Service stopped")


if __name__ == "__main__":
    service = AnalysisService()
    service.run()
