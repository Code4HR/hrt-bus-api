import unittest

def suite():
    suite = unittest.TestSuite()
    suite.addTests(unittest.TestLoader().discover('test'))
    return suite

if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    test_suite = suite()
    runner.run(test_suite)
