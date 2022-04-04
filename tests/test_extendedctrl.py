from multiprocessing.connection import Pipe
from unittest import TestCase
from unittest.mock import patch

from loop import ExtendedCtrl

r_conn, s_conn = Pipe(False)


class TestExtendedCtrl(TestCase):

    @patch('tests.test_extendedctrl.ExtendedCtrl._save_song')
    def test_1(self, mock_method):
        control = ExtendedCtrl(s_conn)
        control.start()
        control.process_message(["_save_song"])
        mock_method.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
