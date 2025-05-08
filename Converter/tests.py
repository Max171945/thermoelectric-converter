import unittest
from decimal import Decimal

from data_classes import Result, Measurement
from teconverter import TEConverter
from thermoexceptions import ThermoException
from thermocouple_table import ThermocoupleTable


class TermocoupleTableTest(unittest.TestCase):

    def setUp(self):
        self.thermocouple_table = ThermocoupleTable()

    def test_get_thermo_emf(self):
        for data in (('0', '0'), ('1700', '17.942'), ('1221.5', '12.2060')):
            with self.subTest(data=data):
                self.assertEqual(self.thermocouple_table.get_thermo_emf(Decimal(data[0])), Decimal(data[1]))


    def test_get_temperature(self):
        for data in (('0', '0'), ( '17.942', '1700'), ('12.2060', '1221.5')):
            with self.subTest(data=data):
                self.assertEqual(self.thermocouple_table.get_temperature(Decimal(data[0])), Decimal(data[1]))

    def test_exceptions(self):
        items = ((ThermoException, self.thermocouple_table.get_thermo_emf, Decimal('-999')),
                (ThermoException, self.thermocouple_table.get_thermo_emf, Decimal('11800')),
                (ThermoException, self.thermocouple_table.get_temperature, Decimal('-99991.0')),
                (ThermoException, self.thermocouple_table.get_temperature, Decimal('99991.0')),
                (Exception, ThermocoupleTable, '')
                )
        for item in items:
            with self.subTest(item=item):
                self.assertRaises(item[0], item[1], item[2])

class TEConverterTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.results = [
            Result(Decimal('22.2'),Decimal('12.0738'), Decimal('0.1262'), Decimal('12.2000'), Decimal('1221.0')),
            Result(Decimal('22.2'), Decimal('12.0642'), Decimal('0.1262'), Decimal('12.1904'), Decimal('1220.2')),
            Result(Decimal('22.7'), Decimal('12.0576'), Decimal('0.1292'), Decimal('12.1868'), Decimal('1219.9')),
        ]

        cls.measurement = [
            Measurement(Decimal('22.2'), Decimal('12.0738')),
            Measurement(Decimal('22.2'), Decimal('12.0642')),
            Measurement(Decimal('22.7'), Decimal('12.0576')),
        ]

    def setUp(self):
        self.converter = TEConverter()

    def test_calculate(self):
        results = self.converter.calculate(*self.measurement)
        for i in range(len(results)):
            with self.subTest(i=i):
                self.assertEqual(results[i], self.results[i])

    def test_generate(self):
        results = self.converter.generate(1220.1)
        self.assertIsInstance(results, list)
        for res in results:
            with self.subTest(res=res):
                self.assertIsInstance(res, Result | str )

    def test_change_thermocouple(self):
        self.assertEqual(self.converter.change_thermocouple_table('ТВР ВР(А)-1'), 'ТВР ВР(А)-1')

    def test_exception(self):
        self.assertRaises(Exception, self.converter.change_thermocouple_table, '')


if __name__ == '__main__':
    unittest.main()
