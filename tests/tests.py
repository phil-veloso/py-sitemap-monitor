

# can connect to internet 
import unittest

from helpers import check_files_exists

class TestSum(unittest.TestCase):
	
    def test_list_int(self):
        """
        Test that it can sum a list of integers
        """
        data = [1, 2, 3]
        result = sum(data)
        self.assertEqual(result, 6)

if __name__ == '__main__':
    unittest.main()

# can create file - Helper.check_exists() 

# can init logger

# can connect to database - Database.open() 

# can create table - Database.create_domain_table()

# can create table - Database.create_siteloop_table()

# can create table - Database.create_url_table()

# can query domains table

# 

#