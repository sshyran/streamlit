import unittest
from unittest.mock import patch, mock_open, MagicMock

from streamlit.runtime import metrics_util

MAC = "mac"
UUID = "uuid"
FILENAME = "/some/id/file"
mock_get_path = MagicMock(return_value=FILENAME)


class MetricsUtilTest(unittest.TestCase):
    def setUp(self):
        self.patch1 = patch("streamlit.file_util.os.stat")
        self.os_stat = self.patch1.start()

    def tearDown(self):
        self.patch1.stop()

    def test_machine_id_v3_from_etc(self):
        """Test getting the machine id from /etc"""
        file_data = "etc"

        with patch(
            "streamlit.runtime.metrics_util.uuid.getnode", return_value=MAC
        ), patch(
            "streamlit.runtime.metrics_util.open",
            mock_open(read_data=file_data),
            create=True,
        ), patch(
            "streamlit.runtime.metrics_util.os.path.isfile"
        ) as path_isfile:

            def path_isfile(path):
                return path == "/etc/machine-id"

            machine_id = metrics_util._get_machine_id_v3()
        self.assertEqual(machine_id, file_data)

    def test_machine_id_v3_from_dbus(self):
        """Test getting the machine id from /var/lib/dbus"""
        file_data = "dbus"

        with patch(
            "streamlit.runtime.metrics_util.uuid.getnode", return_value=MAC
        ), patch(
            "streamlit.runtime.metrics_util.open",
            mock_open(read_data=file_data),
            create=True,
        ), patch(
            "streamlit.runtime.metrics_util.os.path.isfile"
        ) as path_isfile:

            def path_isfile(path):
                return path == "/var/lib/dbus/machine-id"

            machine_id = metrics_util._get_machine_id_v3()
        self.assertEqual(machine_id, file_data)

    def test_machine_id_v3_from_node(self):
        """Test getting the machine id as the mac address"""

        with patch(
            "streamlit.runtime.metrics_util.uuid.getnode", return_value=MAC
        ), patch("streamlit.runtime.metrics_util.os.path.isfile", return_value=False):

            machine_id = metrics_util._get_machine_id_v3()
        self.assertEqual(machine_id, MAC)
