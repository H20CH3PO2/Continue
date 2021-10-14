import Parse_EXEL_file as parser
import unittest


class ParserTest(unittest.TestCase):

    def test_days_between(self):
        self.assertEqual(parser.days_between('01 Январь 2010 00:00', '02 Январь 2010 00:00'), 1)
        self.assertEqual(parser.days_between('02 Январь 2010 00:00', '01 Январь 2010 00:00'), 1)
        self.assertEqual(parser.days_between('01 Январь 2011 00:00', '01 Январь 2010 00:00'), 365)
        self.assertEqual(parser.days_between('01 Январь 2010 00:00', '01 Январь 2010 00:00'), 0)


    def test_add_banches(self):
        task1 = parser.task('1', '2', '')
        task2 = parser.task('2', '3', '1')
        task3 = parser.task('3', '', '2')
        task4 = parser.task('4', '5', '3')

        #Если значения менять НЕ нужно
        self.assertEqual(parser.add_branches_for_2_tasks(task1, task2)[0].id, parser.task('1', '2', '').id)
        self.assertEqual(parser.add_branches_for_2_tasks(task1, task2)[0].followers,
                         parser.task('1', '2', '').followers)
        self.assertEqual(parser.add_branches_for_2_tasks(task1, task2)[0].predecessor,
                         parser.task('1', '2', '').predecessor)

        # Если значения менять НЕ нужно
        self.assertEqual(parser.add_branches_for_2_tasks(task1, task2)[1].id, parser.task('2', '3', '1').id)
        self.assertEqual(parser.add_branches_for_2_tasks(task1, task2)[1].followers,
                         parser.task('2', '3', '1').followers)
        self.assertEqual(parser.add_branches_for_2_tasks(task1, task2)[1].predecessor,
                         parser.task('2', '3', '1').predecessor)

        # Если значения менять нужно
        self.assertEqual(parser.add_branches_for_2_tasks(task3, task4)[0].id, parser.task('3', '4', '2').id)
        self.assertEqual(parser.add_branches_for_2_tasks(task3, task4)[0].followers,
                         parser.task('3', '4', '2').followers)
        self.assertEqual(parser.add_branches_for_2_tasks(task3, task4)[0].predecessor,
                         parser.task('3', '4', '2').predecessor)

        # Если значения менять нужно
        self.assertEqual(parser.add_branches_for_2_tasks(task3, task4)[1].id, parser.task('4', '5', '3').id)
        self.assertEqual(parser.add_branches_for_2_tasks(task3, task4)[1].followers,
                         parser.task('4', '5', '3').followers)
        self.assertEqual(parser.add_branches_for_2_tasks(task3, task4)[1].predecessor,
                         parser.task('4', '5', '3').predecessor)








if __name__ == '__main__':
    unittest.main()