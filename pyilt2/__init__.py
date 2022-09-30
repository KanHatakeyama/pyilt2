# -*- coding: utf-8 -*-
"""
This package contains object classes and functions to access the Ionic Liquids Database - ILThermo (v2.0)
from NIST (Standard Reference Database #147) within Python.

Concept
-------

The :func:`pyilt2.query` function uses the *requests* module to carry out the query on the NIST server.
The resulting *JSON* object is then decoded to a Python dictionary (:doc:`resDict <resdict>`), which serves as input
to create a :class:`pyilt2.result` object.
The result object creates and stores for each hit of the query a :class:`pyilt2.reference` object,
which offers the method :meth:`pyilt2.reference.get` to acquire the full data (:doc:`setDict <setdict>`)
as a  :class:`pyilt2.dataset` object.

Variables
---------

To handle the "problem" with expressing the physical property in a programmatic sense,
there are following module variables accessible:

.. py:data:: prop2abr

   A dictionary with long description as *key* and abbreviation as *value*, like::

    {'Activity': 'a',
     'Adiabatic compressibility': 'kS',
     'Apparent enthalpy': 'Hap',
     'Apparent molar heat capacity': 'capm',
     ...}


.. py:data:: abr2prop

   Obvious the reversed version of :data:`prop2abr` ;)


.. py:data:: properties

   .. deprecated:: 0.9.8
      Use :data:`abr2prop` instead!

   A dictionary where the *key* is an abbreviation and the *value* is a list containing the
   NIST hash and a long description of the respective physical property::

       {"a" :     ["xuYB", "Activity"],
        "phi" :   ["GVwU", "Osmotic coefficient"],
        "Xpeq" :  ["DzMB", "Composition at phase equilibrium"],
        "Xeut"  : ["yfBw", "Eutectic composition"],
        ...}


.. py:data:: abr2key

    This modified dictionary provides the translation between the abbreviation (dict's key)
    of a physical property and the key (dict's value) as used in the http search request.
    Because it already happened that the keys have changed,
    we get those just in time of first usage by a http request.
    It looks like::

        {'Dself': 'wCtj',
         'Dterm': 'LZlp',
         'Dtrac': 'QJLO',
        ...}

    If you don't intend to write your own :func:`query` function, there is no need to access this variable.

Classes & Functions
---------------------
"""

import requests
import numpy as np

from .proplist import prop2abr, abr2prop, abr2key, properties
from .version import __version__

__license__ = "MIT"
__docformat__ = 'reStructuredText'

searchUrl = "http://ilthermo.boulder.nist.gov/ILT2/ilsearch"
dataUrl = "http://ilthermo.boulder.nist.gov/ILT2/ilset"


def query(comp='', numOfComp=0, year='', author='', keywords='', prop=''):
    """ Starts a query on the Ionic Liquids Database from NIST.

    Each web form field is represented by a keyword argument.
    To specify the physical property you have to use the respective :doc:`abbreviation <props>`.
    The function returns a :class:`pyilt2.result` object, whether or not the query makes a hit.

    :param comp: Chemical formula (case-sensitive), CAS registry number, or name (part or full)
    :type comp: str
    :param numOfComp: Number of mixture components. Default '0' means *any* number.
    :type numOfComp: int
    :param year: Publication year
    :type year: str
    :param author: Author's last name
    :type author: str
    :param keywords: Keyword(s)
    :type keywords: str
    :param prop: Physical property by abbreviation. Default '' means *unspecified*.
    :return: result object
    :rtype: :class:`pyilt2.result`
    :raises pyilt2.propertyError: if the abbreviation for physical property is invalid
    :raises pyilt2.queryError: if the database returns an Error on a query
    """
    if prop:
        print(f"search with a property hash key: {prop}")
        """
        if prop not in abr2prop.keys():
            raise propertyError(prop)
        else:
            # prp = properties[prop][0]
            prp = abr2key[prop]
            #prp = "aZvO"
        """
        prp=prop
    else:
        prp = ''
    params = dict(
        cmp=comp,
        ncmp=numOfComp,
        year=year,
        auth=author,
        keyw=keywords,
        prp=prp
    )
    #print(params)
    r = requests.get(searchUrl, params=params)
    resDict = r.json()
    #print(resDict)
    if len(resDict['errors']) > 0:
        e = " *** ".join(resDict['errors'])
        raise queryError(e)
    return result(resDict)


class result(object):
    """ Class to store query results.

    The :class:`.result` object is created by the :func:`pyilt2.query` function.
    Each hit of the query is represented by a :class:`pyilt2.reference` object.
    The build-in function :func:`len` returns the number of hits, respectively
    references stored in the result object.
    It is iterable, so you can simply iterate over references, like:

    .. code-block:: py

        # iterate over references
        for reference in result:
            ...

        # One can also access the individual references as items:
        first_reference = result[0]
        last_reference = result[-1]

    :param resDict: decoded JSON object
    :type resDict: dict
    """

    def __init__(self, resDict):
        self._currentRefIndex = 0
        #: original JSON object from NIST server decoded to a Python dictionary (:doc:`example <resdict>`)
        self.resDict = resDict
        # create reference objects
        self.refs = []
        for ref in self.resDict['res']:
            ref = self._makeRefDict(ref)
            self.refs.append(reference(ref))

    def __len__(self):
        return len(self.refs)

    def __iter__(self):
        return self

    def next(self):
        if self._currentRefIndex < len(self):
            out = self.refs[self._currentRefIndex]
            self._currentRefIndex += 1
            return out
        self._currentRefIndex = 0
        raise StopIteration()

    def __getitem__(self, item):
        return self.refs[item]

    def _makeRefDict(self, refList):
        out = {}
        for i in range(0, len(refList)):
            out[self.resDict['header'][i]] = refList[i]
        return out


class reference(object):
    """ Class to store a reference.

    The :class:`.reference` objects will be created while initiating :class:`pyilt2.result` object.
    It contains just a few meta data. To acquire the full data set, it offers the :meth:`pyilt2.reference.get` method.

    :param refDict: part of ``resDict``
    :type refDict: dict
    """

    def __init__(self, refDict):
        self.refDict = refDict
        #: number of components as integer
        self.numOfComp = 0
        #: names of component names as list of strings
        self.listOfComp = []
        self._parseComp()

    def __str__(self):
        return self.ref

    @property
    def setid(self):
        """NIST setid (hash) as used as input for :class:`pyilt2.dataset`"""
        return self.refDict['setid']

    @property
    def ref(self):
        """
        Reference as in the result table on the website,
        like ``Muster et al. (2018)``, ``Muster and Mann (2018)`` or ``Muster (2018a)``.
        """
        return self.refDict['ref']

    @property
    def sref(self):
        """
        Short reference, like ``MusterEtal2018``, ``MusterMann2018`` or ``Muster2018a``.

        .. note::

            We are very sure about this reference (as derived from :attr:`.ref`) is unique
            within the database. Therefore it can be used as an identifier for a source (publication)
            over multiple requests, for example as BibTeX reference.
        """
        wds = self.ref.split()
        year = wds[-1][1:-1]
        if 'et al.' in self.ref:
            return wds[0] + 'Etal' + year
        elif 'and' in self.ref:
            return wds[0] + wds[2] + year
        else:
            return wds[0] + year

    @property
    def year(self):
        """year of publication as integer"""
        return int(self.ref.split()[-1][1:5])

    @property
    def author(self):
        """1st author’s last name"""
        return self.ref.split()[0]

    @property
    def prop(self):
        """physical property"""
        return self.refDict['prp'].strip()

    @property
    def np(self):
        """Number of data points"""
        return int(self.refDict['np'])

    def _parseComp(self):
        for k in ['nm1', 'nm2', 'nm3']:
            if self.refDict.get(k):
                self.numOfComp += 1
                self.listOfComp.append(self.refDict[k])

    def get(self):
        """ Returns the full data according to this reference.

        :return: Dataset object
        :rtype: :class:`pyilt2.dataset`
        """
        return dataset(self.refDict['setid'])


class dataset(object):
    """ Class to request & store the full data set.

    The :class:`.dataset` object is created by the :meth:`pyilt2.reference.get` method.

    :param setid: NIST setid (hash)
    :type setid: str
    :raises pyilt2.setIdError: if setid is invalid
    """

    def __init__(self, setid):

        #: NIST setid (hash) of this data set
        self.setid = setid

        #: original JSON object from NIST server decoded to a Python dictionary (:doc:`example <setdict>`)
        self.setDict = {}

        #: :class:`numpy.ndarray` containing the data points
        self.data = np.array([])

        #: List containing the **description** for each column of the data set
        self.headerList = []

        #: List containing the **physical property** for each column of the data set
        self.physProps = []

        #: List containing the **physical units** for each column of the data set
        self.physUnits = []

        #: List containing the phase information (if it make sense) for each column of the data set
        self.phases = []

        self._initBySetid()
        self._dataNpArray()
        self._dataHeader()

    def _initBySetid(self):
        r = requests.get(dataUrl, params=dict(set=self.setid))
        # raise HTTPError
        r.raise_for_status()
        # check if response is empty
        if r.text == '':
            raise setIdError(self.setid)
        self.setDict = r.json()

    def _dataHeader(self):
        headerList = self.setDict['dhead']
        cnt = 0
        for col in headerList:
            prop = col[0].replace('<SUP>', '').replace('</SUP>', '')
            if len(col) == 2:
                phase = col[1]
            else:
                phase = None
            if ',' in prop:
                tmp = prop.split(',')
                prop = ''.join(tmp[0:-1])
                units = tmp[-1].strip()
            else:
                units = None
            prop = prop.replace(' ', '_')
            desc = prop
            if phase:
                desc = '{0:s}[{1:s}]'.format(prop, phase)
            if units:
                desc = '{0:s}/{1:s}'.format(desc, units)
            self.headerList.append(desc)
            self.physProps.append(prop)
            self.physUnits.append(units)
            self.phases.append(phase)
            if self._incol[cnt] is 2:
                self.headerList.append('Delta(prev)')
                self.physProps.append('Delta[{0:s}]'.format(prop))
                self.physUnits.append(units)
                self.phases.append(phase)
            cnt += 1
        self.headerLine = '  '.join(self.headerList)

    def _dataNpArray(self):
        raw = self.setDict['data']
        rows = len(raw)
        self._incol = []
        acols = 0
        for c in raw[0]:
            acols += len(c)
            self._incol.append(len(c))

        self.data = np.zeros((rows, acols))
        for i in range(0, len(raw)):
            newrow = [item for sublist in raw[i] for item in sublist]
            for j in range(0, len(newrow)):
                self.data[i][j] = newrow[j]

    @property
    def fullcite(self):
        return '"{0:s}", {1:s}'.format(self.setDict['ref']['title'], self.setDict['ref']['full'])

    @property
    def shape(self):
        """Tuple of :py:attr:`.data` array dimensions."""
        return self.data.shape

    @property
    def np(self):
        """Number of data points"""
        return len(self.data)

    @property
    def listOfComp(self):
        """List of component names as strings."""
        out = []
        for comp in self.setDict['components']:
            out.append(comp['name'])
        return out

    @property
    def numOfComp(self):
        """Number of components as integer."""
        return len(self.setDict['components'])

    def write(self, filename, fmt='%+1.8e', header=None):
        """
        Writes the data set to a text file.

        :param filename: output file name
        :type filename: str
        :param fmt:  str or sequence of strs, (see `numpy.savetxt`_ doc)
        :type fmt: str
        :param header: String that will be written at the beginning of the file. (default from :attr:`.headerList`)
        :type header: str

        .. _numpy.savetxt: https://docs.scipy.org/doc/numpy/reference/generated/numpy.savetxt.html
        """
        if not header:
            header = self.headerLine
        np.savetxt(filename, self.data, fmt=fmt, delimiter=' ',
                   newline='\n', header=header, comments='# ')


class queryError(Exception):
    """Exception if the database returns an Error on a query."""

    def __init__(self, note):
        self.msg = note

    def __str__(self):
        return repr(self.msg)


class propertyError(Exception):
    """Exception if an invalid abbreviation (for physical property) is defined."""

    def __init__(self, prop):
        self.msg = 'Invalid abbreviation "{0:s}" for physical property!'.format(
            prop)

    def __str__(self):
        return repr(self.msg)


class setIdError(Exception):
    """Exception if the set NIST setid (hash) is invalid.

    Because the NIST web server still returns a HTTP status code 200,
    even if the set id is invalid (I would expect here a 404er!),
    this exception class was introduced.
    """

    def __init__(self, setid):
        self.msg = 'SetID "{0:s}" is unknown for NIST!'.format(setid)

    def __str__(self):
        return repr(self.msg)
