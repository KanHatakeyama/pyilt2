# -*- coding: utf-8 -*-
"""
Physical properties

(c) 2018 Frank Roemer; see http://wgserve.de/pyilt2
Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""

import requests

prop2abr = {'Activity': 'a',
            'Adiabatic compressibility': 'kS',
            'Apparent enthalpy': 'Hap',
            'Apparent molar heat capacity': 'capm',
            'Apparent molar volume': 'Vapm',
            'Composition at phase equilibrium': 'Xpeq',
            'Critical pressure': 'Pc',
            'Critical temperature': 'Tc',
            'Density': 'dens',
            'Electrical conductivity': 'econd',
            'Enthalpy': 'H',
            'Enthalpy function {H(T)-H(0)}/T': 'HvT',
            'Enthalpy of dilution': 'Hdil',
            'Enthalpy of mixing of a binary solvent with component': 'Hmix',
            'Enthalpy of transition or fusion': 'Hfus',
            'Enthalpy of vaporization or sublimation': 'Hvap',
            'Entropy': 'S',
            'Equilibrium pressure': 'Peq',
            'Equilibrium temperature': 'Teq',
            'Eutectic composition': 'Xeut',
            'Eutectic temperature': 'Teut',
            'Excess enthalpy': 'Hex',
            'Excess volume': 'Vex',
            'Heat capacity at constant pressure': 'cp',
            'Heat capacity at constant volume': 'cv',
            'Heat capacity at vapor saturation pressure': 'cpe',
            "Henry's Law constant": 'Hc',
            'Interfacial tension': 's',
            'Isobaric coefficient of volume expansion': 'aV',
            'Isothermal compressibility': 'kT',
            'Monotectic temperature': 'Tmot',
            'Normal boiling temperature': 'Tb',
            'Normal melting temperature': 'Tm',
            'Osmotic coefficient': 'phi',
            'Ostwald coefficient': 'L',
            'Partial molar enthalpy': 'Hpm',
            'Partial molar volume': 'Vpm',
            'Refractive index': 'n',
            'Relative permittivity': 'rperm',
            'Self-diffusion coefficient': 'Dself',
            'Speed of sound': 'sos',
            'Surface tension liquid-gas': 'slg',
            'Thermal conductivity': 'Tcond',
            'Thermal diffusivity': 'Dterm',
            'Tieline': 'tline',
            'Tracer diffusion coefficient': 'Dtrac',
            'Upper consolute composition': 'Xucon',
            'Upper consolute pressure': 'Pucon',
            'Upper consolute temperature': 'Tucon',
            'Viscosity': 'visc'}

abr2prop = {v: k for k, v in prop2abr.items()}


class __abr2keyDict(dict):
    """
    This modified dictionary class provides the translation between the abbreviation (dict's key)
    of a physical property and the key (dict's value) as used in the http search request.
    Because it already happened that the keys have changed,
    we get those just in time of first usage by a http request.
    """

    proplistUrl = 'https://ilthermo.boulder.nist.gov/ILT2/ilprpls'

    def __polulate(self):
        r = requests.get(self.proplistUrl)
        prpDict = r.json()
        prpNames = []
        prpKeys = []
        for pcls in prpDict['plist']:
            pcls['name'] = map(str.strip, pcls['name'])
            prpNames += pcls['name']
            prpKeys += pcls['key']
        prop2key = dict(zip(prpNames, prpKeys))
        for prpName, prpKey in prop2key.items():
            self.__dict__[prop2abr[prpName]] = prpKey

    def __pkcache(func):
        def func_wrapper(self, *args):
            if len(self.__dict__) is 0:
                self.__polulate()
            return func(self, *args)
        # this we do for sphinx.autodoc!
        func_wrapper.__doc__ = func.__doc__
        return func_wrapper

    @__pkcache
    def __repr__(self):
        return repr(self.__dict__)

    @__pkcache
    def __len__(self):
        return len(self.__dict__)

    @__pkcache
    def __getitem__(self, prpAbr):
        return self.__dict__[prpAbr]

    @__pkcache
    def keys(self):
        return self.__dict__.keys()

    @__pkcache
    def values(self):
        return self.__dict__.values()

    @__pkcache
    def items(self):
        return self.__dict__.items()


#abr2key = __abr2keyDict()
abr2key = {v: k for k, v in prop2abr.items()}

# physical properties 'abbr.->[hash, long]'
properties = {
    'Dself': ['wCtj', 'Self-diffusion coefficient'],
    'Dterm': ['LZlp', 'Thermal diffusivity'],
    'Dtrac': ['QJLO', 'Tracer diffusion coefficient'],
    'H': ['wRMb', 'Enthalpy'],
    'Hap': ['KuRZ', 'Apparent enthalpy'],
    'Hc': ['TZRG', "Henry's Law constant"],
    'Hdil': ['uChD', 'Enthalpy of dilution'],
    'Hex': ['nYML', 'Excess enthalpy'],
    'Hfus': ['Exvj', 'Enthalpy of transition or fusion'],
    'Hmix': ['Xndy', 'Enthalpy of mixing of a binary solvent with component'],
    'Hpm': ['hrKG', 'Partial molar enthalpy'],
    'HvT': ['jSGu', 'Enthalpy function {H(T)-H(0)}/T'],
    'Hvap': ['ftHP', 'Enthalpy of vaporization or sublimation'],
    'L': ['IvMf', 'Ostwald coefficient'],
    'Pc': ['Msbg', 'Critical pressure'],
    'Peq': ['qhbo', 'Equilibrium pressure'],
    'Pucon': ['fGxt', 'Upper consolute pressure'],
    'S': ['yfIP', 'Entropy'],
    'Tb': ['mfvC', 'Normal boiling temperature'],
    'Tc': ['nOoz', 'Critical temperature'],
    'Tcond': ['MYsr', 'Thermal conductivity'],
    'Teq': ['CkHK', 'Equilibrium temperature'],
    'Teut': ['DFpj', 'Eutectic temperature'],
    'Tm': ['kZMO', 'Normal melting temperature'],
    'Tmot': ['xNNb', 'Monotectic temperature'],
    'Tucon': ['THUU', 'Upper consolute temperature'],
    'Vapm': ['aBBm', 'Apparent molar volume'],
    'Vex': ['ksvJ', 'Excess volume'],
    'Vpm': ['jSTk', 'Partial molar volume'],
    'Xeut': ['QRlf', 'Eutectic composition'],
    'Xpeq': ['Fptx', 'Composition at phase equilibrium'],
    'Xucon': ['zThS', 'Upper consolute composition'],
    'a': ['GIOY', 'Activity'],
    'aV': ['qNxb', 'Isobaric coefficient of volume expansion'],
    'capm': ['YpPw', 'Apparent molar heat capacity'],
    'cp': ['tYhZ', 'Heat capacity at constant pressure'],
    'cpe': ['LiNC', 'Heat capacity at vapor saturation pressure'],
    'cv': ['VRCC', 'Heat capacity at constant volume'],
    'dens': ['VehR', 'Density'],
    'econd': ['fnRH', 'Electrical conductivity'],
    'kS': ['EQiy', 'Adiabatic compressibility'],
    'kT': ['waKp', 'Isothermal compressibility'],
    'n': ['Agpv', 'Refractive index'],
    'phi': ['FXOy', 'Osmotic coefficient'],
    'rperm': ['YSLP', 'Relative permittivity'],
    's': ['sxQZ', 'Interfacial tension'],
    'slg': ['exok', 'Surface tension liquid-gas'],
    'sos': ['Gjrc', 'Speed of sound'],
    'tline': ['IwRh', 'Tieline'],
    'visc': ['AJfy', 'Viscosity']}
