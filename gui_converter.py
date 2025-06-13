from decimal import Decimal
from re import fullmatch

import wx
from wx.lib.agw.buttonpanel import BoxSizer

from Converter.constants import TEMP_FREE_END, STANDARD_DEVIATION_TEMP_FREE_END
from Converter.constants import THERMOCOUPLES, DEFAULT_THERMOCOUPLE, QUANTITY, STANDARD_DEVIATION_TEMP
from Converter.data_classes import Measurement, Result
from Converter.teconverter import TEConverter

LINKS: list[str] = list(THERMOCOUPLES.keys())
DEFAULT_INDEX = LINKS.index(DEFAULT_THERMOCOUPLE)
WIDTH: int = 800
HEIGHT: int = 800
MIN_MEASUREMENTS: int = 1
MAX_MEASUREMENTS: int = 7
RES_WIDTH: int = 250
RES_HEIGHT: int = 250
BORDER: int = 10
DELTA_MESSAGE: str = f'∆T  ='
LINE: str = '\u2500' * 5
PATTERN: str = r'[+-]?([0-9]+([.][0-9]*)?|[.][0-9]+)'


class FloatPointValidator(wx.Validator):
    """
    Validator for floating-point numbers.
    """

    def __init__(self):
        super().__init__()

    def Clone(self):
        return FloatPointValidator()

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def Validate(self, parent: wx.TextCtrl):
        num = parent.GetValue()
        if fullmatch(PATTERN, num):
            return True
        wx.MessageBox(f'Enter a floating-point number (in the 0.0 or 0 format).\n '
                      f'You have entered: {num if num else "None"}',
                      'Input error!')
        return False


class ThermoPanel(wx.Panel):
    """
    Creates a panel with a form for measurements and results.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        hbox = wx.StaticBoxSizer(wx.VERTICAL, self)

        box = wx.GridBagSizer(5, 5)

        temp_text = wx.StaticText(self, label='Temperature, °C:')
        box.Add(temp_text, pos=(0, 0), flag=wx.ALL|wx.EXPAND, border=BORDER)

        self.temp = wx.TextCtrl(self, style=wx.TE_RIGHT, validator=FloatPointValidator())
        box.Add(self.temp, pos=(0, 1), flag=wx.EXPAND)

        thermo_emf_text = wx.StaticText(self, label='Thermo-emf, mV:')
        box.Add(thermo_emf_text, pos=(1, 0), flag=wx.ALL|wx.EXPAND, border=BORDER)

        self.thermo_emf = wx.TextCtrl(self, style=wx.TE_RIGHT, validator=FloatPointValidator())
        box.Add(self.thermo_emf, pos=(1, 1), flag=wx.EXPAND)

        res_text = wx.StaticText(self, label='Result:')
        box.Add(res_text, pos=(2, 0), flag=wx.ALL|wx.EXPAND, border=BORDER)

        self.res = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_RIGHT)
        box.Add(self.res, pos=(2, 1), flag=wx.TOP|wx.BOTTOM|wx.EXPAND, border=BORDER)
        box.AddGrowableRow(2)

        hbox.Add(box, proportion=1, flag=wx.ALL|wx.EXPAND, border=BORDER)

        self.SetSizer(hbox)

    def get_measurement(self):
        """
        Returns the value of the measured temperature of free end and thermo-emf.
        """
        return self.temp.GetValue(), self.thermo_emf.GetValue()

    def set_temperature(self, temperature: str):
        """
        Sets the value of temperature of free end.
        """
        self.temp.SetValue(temperature)

    def set_thermo_emf(self, thermo_emf: str):
        """
        Sets the value of thermo-emf.
        """
        self.thermo_emf.SetValue(thermo_emf)

    def set_result(self, result: str):
        """
        Sets the result of the calculation.
        """
        self.res.SetValue(result)

    def clear_result(self, generate_mode: bool = False):
        """
        Clears the result of the calculation.
        """
        self.res.Clear()
        if generate_mode:
            self.temp.Clear()
            self.thermo_emf.Clear()

    def set_read_only_mode(self):
        """
        Sets the read-only mode.
        """
        self.temp.SetWindowStyle(wx.TE_READONLY|wx.TE_RIGHT)
        self.thermo_emf.SetWindowStyle(wx.TE_READONLY|wx.TE_RIGHT)



class BasePanel(wx.Panel):
    """
    A base class containing methods for building a panel with the results of calculations or generation.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.converter = TEConverter()
        except Exception as e:
            message = f'Error creating the converter: {e}'
            error_dial = wx.MessageDialog(None, message, 'Error', style=wx.ICON_ERROR)
            error_dial.ShowModal()
            exit()

        self.panels: list[ThermoPanel] = []

        self.generate_mode = False
        self._res_box = None
        self._delta = None

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vbox)

    def create_type_thermocouple_and_measurements(self):
        """
        Creates a field for selecting the type of thermocouple and a slider for selecting the number of measurements.
        """

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        type_thermocouple = wx.StaticText(self, label='Type of thermocouple:')
        hbox.Add(type_thermocouple, flag=wx.ALL, border=BORDER)

        thermocouples = wx.ComboBox(self, choices=LINKS, style=wx.CB_READONLY)
        thermocouples.SetSelection(DEFAULT_INDEX)
        thermocouples.Bind(wx.EVT_COMBOBOX, self._change_converter)
        hbox.Add(thermocouples, flag=wx.RIGHT, border=BORDER * 3)

        number_measurements = wx.StaticText(self, label='Number of measurements:')
        hbox.Add(number_measurements, flag=wx.ALL, border=BORDER + 2)

        measurements = wx.SpinCtrl(self, value=str(QUANTITY), min=MIN_MEASUREMENTS, max=MAX_MEASUREMENTS)
        measurements.Bind(wx.EVT_SPINCTRL, self._update_result_panels)
        hbox.Add(measurements, flag=wx.TOP, border=BORDER // 5)

        self.vbox.Add(hbox, flag=wx.ALL, border=BORDER)


    def _create_panels(self, parent: wx.Window, sizer: wx.Sizer, num: int, size: wx.Size| tuple[int, int]):
        """
        Creates thermo-panels.
        """
        for i in range(num):
            panel = ThermoPanel(parent, size=size)
            if self.generate_mode: panel.set_read_only_mode()
            sizer.Add(panel, flag=wx.RIGHT, border=BORDER)
            self.panels.append(panel)

    def create_result_panels(self):
        """
        Creates panels with results.
        """
        self._res_box = wx.BoxSizer(wx.HORIZONTAL)
        self._create_panels(self, self._res_box, QUANTITY, wx.Size(RES_WIDTH, RES_WIDTH))
        self.vbox.Add(self._res_box, flag=wx.ALL, border=BORDER)

    def create_delta(self):
        """
        Creates an element with the output value of the difference between the maximum and minimum temperature.
        """
        self._delta = wx.StaticText(self, label=DELTA_MESSAGE)
        self.vbox.Add(self._delta, flag=wx.ALL, border=BORDER)

    def clear_delta(self):
        """
        Clears the value of the difference between the maximum and minimum temperature.
        """
        if self._delta: self._delta.SetLabel(DELTA_MESSAGE)

    def set_delta(self, value: str):
        """
        Sets the value of the difference between the maximum and minimum temperature.
        """
        if self._delta: self._delta.SetLabel(value)


    def _change_converter(self, event):
        """
        Changes the converter type.
        """

        combobox = event.GetEventObject()

        for panel in self.panels: panel.clear_result(generate_mode=self.generate_mode)
        self.clear_delta()

        try:
            self.converter.change_thermocouple_table(combobox.GetValue())
        except Exception as e:
            message = f'Error changing the converter: {e}'
            error_dial = wx.MessageDialog(None, message, 'Error', style=wx.ICON_ERROR)
            error_dial.ShowModal()
            combobox.SetValue(self.converter.get_thermocouple())

    def _update_result_panels(self, event):
        """
        Updates panels with results.
        """
        spin = event.GetEventObject()
        if self._res_box is None:
            return
        if not self._res_box.IsEmpty():
            for i in range(len(self.panels)-1, -1, -1):
                self._res_box.Hide(i)
                self._res_box.Remove(i)
        for panel in self.panels: panel.Destroy()
        self.panels.clear()
        self._create_panels(self, self._res_box, spin.GetValue(), wx.Size(RES_WIDTH, RES_WIDTH))
        self.clear_delta()
        self.vbox.Layout()
        self.Fit()

    def output_results(self, results: list[Result | str], generate: bool = False):
        """
        Outputs the result of a calculation or generation.
        """
        for panel, res in zip(self.panels, results):
            if isinstance(res, Result):
                if generate:
                    panel.set_temperature(str(res.temperature_free_end))
                    panel.set_thermo_emf(str(res.thermo_emf))
                res_message = (f'{res.thermo_emf:8}  \n+  {res.correction:8}  \n'
                               f'{LINE}  \n{res.result_thermo_emf:8}  \n\n{res.temperature:8}  ')
                panel.set_result(res_message)
            else:
                panel.clear_result(generate_mode=generate)
                self.clear_delta()
                wx.MessageBox(res, 'Error', style=wx.OK)

        if all([isinstance(_, Result) for _ in results]) and results:
            max_temp, min_temp = max(results).temperature, min(results).temperature
            self.set_delta(f'∆T  =  {max_temp}°C   -   {min_temp}°C   =   {max_temp-min_temp}°C')


class CalcPanel(BasePanel):
    """
    The panel for the calculation mode.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.create_type_thermocouple_and_measurements()

        self.vbox.Add(wx.StaticLine(self), flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=BORDER)

        self.create_result_panels()

        self.vbox.Add(wx.StaticText(self), proportion=1, flag=wx.EXPAND)

        self.vbox.Add(wx.StaticLine(self), flag=wx.EXPAND | wx.ALL, border=BORDER)

        self.create_delta()

        self.vbox.Add(wx.StaticLine(self), flag=wx.EXPAND | wx.ALL, border=BORDER)


        button = wx.Button(self, label='Calculate')
        self.vbox.Add(button, flag=wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM | wx.RIGHT, border=BORDER * 2)
        self.Bind(wx.EVT_BUTTON, self.calculate)

    def calculate(self, event):
        """
        The handler that calls the calculation of the entered measurements.
        """

        measurements = []

        for panel in self.panels:
            if not panel.Validate():
                panel.clear_result()
                self.clear_delta()
                return
            temp, thermo_emf = panel.get_measurement()
            measurements.append(Measurement(Decimal(temp), Decimal(thermo_emf)))

        results = self.converter.calculate(*measurements)

        self.output_results(results)


class GenPanel(BasePanel):
    """
    The panel for generation mode.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.generate_mode = True

        self.create_type_thermocouple_and_measurements()

        hbox = BoxSizer(wx.HORIZONTAL)
        temperature_text = wx.StaticText(self, label='Temperature, °C:')
        hbox.Add(temperature_text, flag=wx.LEFT | wx.RIGHT | wx.TOP, border=BORDER)
        self.temperature = wx.TextCtrl(self, style=wx.TE_RIGHT, validator=FloatPointValidator())
        hbox.Add(self.temperature, flag=wx.LEFT, border=BORDER*4)
        self.vbox.Add(hbox, flag=wx.ALL, border=BORDER)

        panel = wx.Panel(self)
        st_box = wx.StaticBoxSizer(wx.VERTICAL, panel, label='Mode:')
        r_box = wx.BoxSizer(wx.HORIZONTAL)
        self.standard = wx.RadioButton(panel, label='Standard', size=wx.Size(100, 48))
        r_box.Add(self.standard)
        self.extended = wx.RadioButton(panel, label='Extended', size=wx.Size(100, 48))
        r_box.Add(self.extended)
        st_box.Add(r_box, flag=wx.ALL|wx.EXPAND, border=BORDER//5)
        self.Bind(wx.EVT_RADIOBUTTON, self.change_mode)

        self.box_panel = wx.Panel(panel)
        box = wx.GridBagSizer(0, 0)
        stand_dev_temp_text = wx.StaticText(self.box_panel, label='Standard deviation of temperature:')
        box.Add(stand_dev_temp_text, pos=(0,0), flag=wx.ALL, border=BORDER)
        self.stand_dev_temp = wx.TextCtrl(self.box_panel, value=str(STANDARD_DEVIATION_TEMP),
                                     style=wx.TE_RIGHT, validator=FloatPointValidator())
        box.Add(self.stand_dev_temp, pos=(0, 1), flag=wx.RIGHT, border=BORDER)
        temp_free_end_text = wx.StaticText(self.box_panel, label='Temperature of free end, °C:')
        box.Add(temp_free_end_text,  pos=(0,2), flag=wx.ALL, border=BORDER)
        self.temp_free_end = wx.TextCtrl(self.box_panel, value=str(TEMP_FREE_END),
                                    style=wx.TE_RIGHT, validator=FloatPointValidator())
        box.Add(self.temp_free_end, pos=(0, 3))
        stand_dev_temp_free_end_text = wx.StaticText(self.box_panel, label='Standard deviation of free end temperature:')
        box.Add(stand_dev_temp_free_end_text, pos=(1,0), flag=wx.ALL, border=BORDER)
        self.stand_dev_temp_free_end = wx.TextCtrl(self.box_panel, value=str(STANDARD_DEVIATION_TEMP_FREE_END),
                                              style=wx.TE_RIGHT, validator=FloatPointValidator())
        box.Add(self.stand_dev_temp_free_end, pos=(1,1))
        self.box_panel.SetSizer(box)
        self.box_panel.Disable()

        st_box.Add(self.box_panel, flag=wx.RIGHT | wx.LEFT | wx.BOTTOM | wx.EXPAND, border=BORDER)
        panel.SetSizer(st_box)

        self.vbox.Add(panel, flag=wx.ALL |wx.EXPAND, border=BORDER)

        self.vbox.Add(wx.StaticLine(self), flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP, border=BORDER)

        self.create_result_panels()

        self.vbox.Add(wx.StaticText(self), proportion=1, flag=wx.EXPAND)

        self.vbox.Add(wx.StaticLine(self), flag=wx.EXPAND | wx.ALL, border=BORDER)

        self.create_delta()

        self.vbox.Add(wx.StaticLine(self), flag=wx.EXPAND | wx.ALL, border=BORDER)

        button = wx.Button(self, label='Generate')
        self.vbox.Add(button, flag=wx.ALIGN_RIGHT | wx.TOP | wx.BOTTOM | wx.RIGHT, border=BORDER * 2)
        self.Bind(wx.EVT_BUTTON, self.generate)

    def generate(self, event):
        """
        The handler that is called in generation mode.
        """
        if not self.box_panel.Validate() or not self.temperature.Validate():
            for panel in self.panels: panel.clear_result(generate_mode=self.generate_mode)
            self.clear_delta()
            return

        temperature = float(self.temperature.GetValue())
        quantity = len(self.panels)
        std_temp = float(self.stand_dev_temp.GetValue())
        temp_free_end = float(self.temp_free_end.GetValue())
        std_free_end = float(self.stand_dev_temp_free_end.GetValue())

        results = self.converter.generate(temperature, quantity, std_temp, temp_free_end, std_free_end)

        self.output_results(results, generate=self.generate_mode)


    def change_mode(self, event):
        """
        Changes the generation mode.
        """
        btn = event.GetEventObject()
        if btn == self.standard:
            self.box_panel.Disable()
            self.stand_dev_temp.SetValue(str(STANDARD_DEVIATION_TEMP))
            self.temp_free_end.SetValue(str(TEMP_FREE_END))
            self.stand_dev_temp_free_end.SetValue(str(STANDARD_DEVIATION_TEMP_FREE_END))
        elif btn == self.extended:
            self.box_panel.Enable()



class TEConverterFrame(wx.Frame):
    """
    The main window.
    """

    def __init__(self, parent, title):
        super().__init__(parent, title=title, size=wx.Size(WIDTH, HEIGHT))

        tabs = wx.Notebook(self, id=wx.ID_ANY)
        tabs.SetPadding(wx.Size(20, 5))

        self.calc_panel = CalcPanel(tabs)
        tabs.InsertPage(0, self.calc_panel, 'Calculate', select=True)

        self.generate_panel = GenPanel(tabs)
        tabs.InsertPage(1, self.generate_panel, 'Generate')


if __name__ == '__main__':
    app = wx.App()
    frame = TEConverterFrame(parent=None, title='TEConverter')
    frame.Show()
    app.MainLoop()