import unittest
from unittest.mock import patch, MagicMock
import json
import os

from speed_layer.producer import SpeedLayerProducer

TEST_JSON_PATH = os.path.join(os.path.dirname(__file__), 'test_data.json')

class TestSpeedLayerProducer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with open(TEST_JSON_PATH, 'r') as f:
            cls.test_messages = json.load(f)

    @patch('speed_layer.producer.KafkaProducer')
    def test_send_all_endpoints(self, mock_kafka_producer_cls):
        # Setup Mock KafkaProducer and its future response
        mock_producer = MagicMock()
        future = MagicMock()
        future.get.return_value = None
        mock_producer.send.return_value = future
        mock_kafka_producer_cls.return_value = mock_producer

        producer = SpeedLayerProducer()
        send_count = 0
        for msg in self.test_messages:
            raw = msg.get('raw_data', {})
            endpoint = raw.get('endpoint', msg.get('endpoint_type'))
            data = raw.get('data', {})
            result = producer.send_to_kafka(endpoint, data)
            self.assertTrue(result)
            send_count += 1

        self.assertEqual(send_count, len(self.test_messages))
        self.assertEqual(mock_producer.send.call_count, len(self.test_messages))


if __name__ == '__main__':
    unittest.main()
