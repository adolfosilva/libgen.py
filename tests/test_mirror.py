import unittest.mock
from libgen.mirrors import Mirror,GenLibRusEc,LibGenPw
import libgen.downloaders
import vcr

my_vcr = vcr.VCR(
    cassette_library_dir='tests/fixtures/cassettes'
)

# if you are rewriting cassettes don't forget to use torify if you are have trouble to access libraries without Tor
# e.g. $ torify py.test tests/
@my_vcr.use_cassette()
@unittest.mock.patch('libgen.downloaders.save_file')
def test_mirror_interactive_run(mock_save_file):
    with unittest.mock.patch('builtins.input', return_value="2258882"):
        with unittest.mock.patch('os.get_terminal_size', return_value=(80, 80)):
            # http://www.oapen.org/search?identifier=633792;keyword=mathematics
            GenLibRusEc("Stephen Siklos Advanced Problems in Mathematics: Preparing for University").run()

    assert mock_save_file.called

@my_vcr.use_cassette("tests/fixtures/cassettes/test_mirror_interactive_run")
@unittest.mock.patch('libgen.downloaders.save_file')
def test_mirror_non_interactive_run(mock_save_file):
    # http://www.oapen.org/search?identifier=633792;keyword=mathematics
    GenLibRusEc("Stephen Siklos Advanced Problems in Mathematics: Preparing for University").run(non_interactive=True)

    assert mock_save_file.called
