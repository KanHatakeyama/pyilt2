#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple example for a search & report tool using the pyILT2 library.

(c) 2018 Frank Roemer; see http://wgserve.de/pyilt2
Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
"""

from __future__ import print_function
from . import (properties, prop2abr, abr2prop, query, __version__)
import argparse
import datetime
import sys
import time
import threading
import os
import requests

# version of the search & report tool
__prgversion__ = '1.1'
__prgdescrpt__ = 'A search and report tool for the ILThermo v2.0 database from NIST (http://ilthermo.boulder.nist.gov).'


# ===============================================================================
# local classes and functions
# ===============================================================================

class Spinner:
    """A class providing a spinning courser for cli tools."""
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        """Start the spinner."""
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        """Stop the spinner."""
        self.busy = False
        time.sleep(self.delay)

# create a spinner object for some of the following functions
spinner = Spinner()


def printPropAbbrList():
    """
    Print a table, showing the physical properties which can be addressed in a query,
    and the respective *abbreviation* which is used in the :func:`pyilt2.query` function, to *stdout*::

         Abbr.  Property
        ------  -----------------------------------------
         Dself  Self-diffusion coefficient
         Dterm  Thermal diffusivity
         Dtrac  Tracer diffusion coefficient
             H  Enthalpy
           Hap  Apparent enthalpy
           ...  ...

    """
    print ( "%6s  %s" % ('Abbr.','Property') )
    print ('------  -----------------------------------------')
    for key in sorted(abr2prop):
        print ( "%6s  %s" % (key, abr2prop[key]) )


def printResultTable(resObj):
    """
    Print a result table (similar to the web version) to *stdout*, like::

           # ref                  prop     np components(s)
        ---- -------------------- ------ ---- ----------------------------------------
           0 Krolikowska2012      dens     65 1-ethyl-3-methylimidazolium thiocyanate
           1 Klomfar2015a         dens     37 1-ethyl-3-methylimidazolium thiocyanate
           2 Freire2011           dens     18 1-ethyl-3-methylimidazolium thiocyanate
           3 Neves2013b           dens     18 1-ethyl-3-methylimidazolium thiocyanate

    """
    print('\n   # {0:20s} {1:6s} {2:>4s} {3:s}'.format('ref', 'prop', 'np', 'components(s)'))
    print('{0:s} {1:s} {2:s} {3:s} {4:s}'.format('-' * 4, '-' * 20, '-' * 6, '-' * 4, '-' * 40))
    for i in range(0, len(resObj)):
        r = resObj[i]
        print('{0:4d} {1:20s} {2:6s} {3:4d} {4:s}'.
              format( i, r.sref, prop2abr[r.prop], r.np, ' | '.join(r.listOfComp) ) )


def metaDataStr(datObj):
    """
    Returns the meta data of an :class:`pyilt2.dataset` object as a *string*, like::

        Property:
          Specific density
        Reference:
          "Densities, isobaric expansivities and isothermal compressibilities [...].",
          Krolikowska, M.; Hofman, T. (2012) Thermochim. Acta 530, 1-6.
        Component(s):
          1) 1-ethyl-3-methylimidazolium thiocyanate
        Method: Vibrating tube method
        Phase(s): Liquid
        Data columns:
          1) Temperature/K
          2) Pressure/kPa
        ...

    :param datObj: dataset object
    :type datObj: :class:`pyilt2.dataset`
    :return: meta data
    :rtype: str
    """
    out =  'Property:\n  {0:s}\n'.format(datObj.setDict['title'].split(':')[-1].strip())
    out += 'Reference:\n'
    out += '  "{0:s}",\n'.format(datObj.setDict['ref']['title'])
    out += '  {0:s}\n'.format(datObj.setDict['ref']['full'])
    out += 'Component(s):\n'
    for i in range(0, datObj.numOfComp):
        out += '  {0:d}) {1:s}\n'.format(i+1, datObj.listOfComp[i])
    if datObj.setDict['expmeth']:
        out += 'Method: {0:s}\n'.format(datObj.setDict['expmeth'])
    out += 'Phase(s): {0:s}\n'.format(', '.join(datObj.setDict['phases']))
    if datObj.setDict['solvent']:
        out += 'Solvent: {0:s}\n'.format(datObj.setDict['solvent'])
    out += 'Data columns:\n'
    for i in range(0, len(datObj.headerList)):
        out += '  {0:d}) {1:s}\n'.format(i+1, datObj.headerList[i])
    out += 'Data points: {0:d}\n'.format(datObj.np)
    out += 'ILT2 setid: {0:s}\n'.format(datObj.setid)
    return out


def writeReport(listOfDataSets, reportDir=None, resDOI=False, verbose=False):
    dtnow = datetime.datetime.now()
    if not reportDir:
        reportDir = 'pyilt2report_' + dtnow.strftime("%Y-%m-%d_%H:%M:%S")
    os.mkdir(reportDir)
    if verbose:
        print('\nWrite report to folder: '+reportDir)
        print(' << report.txt')
    rep = open(reportDir + '/report.txt', 'w')
    rep.write(dtnow.strftime("%d. %b. %Y (%H:%M:%S)") + '\n')
    rep.write('-' * 24 + '\n')
    for i in range(0, len(listOfDataSets)):
        dataSet = listOfDataSets[i]
        dataFile = 'ref{0:d}.dat'.format(i)
        # write data file
        dataSet.write(reportDir + '/' + dataFile)
        if verbose:
            print(' << {0:s} [{1:s}]'.format(dataFile, dataSet.setid))
        # write meta data to report file
        rep.write('\nRef. #{0:d}\n'.format(i, dataSet.setid))
        rep.write('=' * 10 + '\n')
        rep.write( metaDataStr(dataSet) )
        if resDOI:
            if verbose:
                print(' >> resolve DOI ... ', end='')
                spinner.start()
            try:
                (doi, url, score) = citation2doi(dataSet.fullcite)
            except:
                if verbose:
                    spinner.stop()
                e = sys.exc_info()[1]
                print('Error: {0:s}'.format(str(e)))
            else:
                if verbose:
                    spinner.stop()
                    print('\b {0:s} (score: {1:f}) done!'.format(doi, score))
                rep.write('DOI: {0:s} (score: {1:f})\n'.format(doi, score))
                rep.write('URL: {0:s}\n'.format(url))
    rep.close()
    return reportDir


def doicache( func ):
    """ Decorator function for :func:`citation2doi` providing a cache. """
    _doicache = {}
    def func_wrapper( citation ):
        _hash = hash(citation)
        if _hash in _doicache.keys():
            return _doicache[_hash]
        else:
            _doicache[_hash] = func(citation)
            return _doicache[_hash]
    # this we do for sphinx.autodoc!
    func_wrapper.__doc__= func.__doc__
    return func_wrapper

@doicache
def citation2doi( citation ):
    """
    Resolves a citation string like the respective DOI ,URL and a score.
    Therefore we use Crossref's REST API: https://github.com/CrossRef/rest-api-doc

    .. code-block:: py

        >>> cite='Lennard-Jones, J. E. "Cohesion" Proc. Phys. Soc., 1931, 43, 461-482'
        >>> print( citation2doi(cite) )
        ('10.1088/0959-5309/43/5/301',
         'http://dx.doi.org/10.1088/0959-5309/43/5/301',
         69.865814)

    :param citation: citation in *natural* form
    :type citation: str
    :return: DOI, URL, score
    :rtype: tuple
    """
    url = 'https://api.crossref.org/works'
    payload = {'query.bibliographic': citation}
    r = requests.get(url, params=payload)
    r = r.json()['message']['items'][0]
    return ( r['DOI'], r['URL'], r['score'] )


def cliQuery(comp='', numOfComp=0, year='', author='', keywords='', prop='', verbose=True):
    """
    This is a wapper function for :func:`pyilt2.query` which is suitable for cli tools.
    It shows a spinning cursor while waiting for the answer from the web server and includes error handling.

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
    :type prop: str
    :param verbose: Show messages and spinning cursor while waiting.
    :type verbose: bool
    :return: result object
    :rtype: :class:`pyilt2.result`
    """
    resObj=None
    if verbose:
        print('Make query to NIST... ', end='')
        spinner.start()
    try:
        resObj = query(comp=comp,
                              numOfComp=numOfComp,
                              year=year,
                              author=author,
                              keywords=keywords,
                              prop=prop)
    except:
        if verbose:
            spinner.stop()
        e = sys.exc_info()[1]
        print('Error: {0:s}'.format(str(e)))
        exit(1)
    else:
        if verbose:
            spinner.stop()
            print('\b done! ({0:d} hits)'.format(len(resObj)))
    return resObj


def getAllData(resObj, verbose=False):
    """
    Requests the data sets for all references of a :class:`pyilt2.result`
    object and returns them as a list.

    :param resObj: A result object
    :type resObj:  :class:`pyilt2.result`
    :param verbose: Show messages and spinning cursor while waiting.
    :return: List of :class:`pyilt2.dataset` objects
    """
    dataSets = []
    if verbose:
        print('\nRequest data sets from NIST:')
    for i in range(0, len(resObj)):
        if verbose:
            print(' >> {0:s} [{1:s}] ... '.format(resObj[i].ref, resObj[i].setid), end='')
            spinner.start()
        try:
            dataSets.append(resObj[i].get())
        except:
            if verbose:
                spinner.stop()
            e = sys.exc_info()[1]
            print('Error: {0:s}'.format(str(e)))
            exit(1)
        else:
            if verbose:
                spinner.stop()
                print('\b done!')
    return dataSets


def _getArgParser():
    """Argument parser for pyilt2report cli tool."""
    parser = argparse.ArgumentParser(description=__prgdescrpt__,
                                     epilog="Type 'man pyilt2report' for more information.")
    parser.add_argument('-c', type=str, metavar='str',
                        help='chemical formula, CAS registry number, or name (part or full)', default='')
    parser.add_argument('-n', type=int, metavar='0',
                        help='number of mixture components. Default: 0 = any number.', default=0)
    parser.add_argument('-y', type=str, metavar='2018',
                        help='publication year', default='')
    parser.add_argument('-a', type=str, metavar='name',
                        help='author’s last name', default='')
    parser.add_argument('-k', type=str, metavar='str',
                        help='keyword(s)', default='')
    parser.add_argument('-p', type=str, metavar='prop',
                        help='physical property by abbreviation.', default=None)
    parser.add_argument('-o', '--out', type=str, metavar='dir',
                        help='result folder for output files', default=None)
    parser.add_argument('--doi', action='store_true',
                        help='try to resolve DOI from citation (experimental!)', default=False)
    parser.add_argument('--auto', action='store_true',
                        help='dont ask if to proceed creating report', default=False)
    parser.add_argument('--props', action='store_true',
                        help='show properties abbreviations and exit', default=False)
    parser.add_argument('--version', action='version',
                        version="%(prog)s " + __prgversion__ + " (pyilt2 " + __version__ + ")")
    return parser


# ===============================================================================
# run
# ===============================================================================
def run():
    """CLI main entry point."""

    # get command line arguments
    parser = _getArgParser()
    args = parser.parse_args()

    # show properties abbreviations and exit (option: --props)
    if args.props:
        printPropAbbrList()
        exit(0)

    # check the 'phys. property' search option
    sprop = ''
    if args.p:
        if args.p not in abr2prop.keys():
            print('Error! Invalid abbreviation "{0:s}" for physical property.'.format(args.p))
            exit(1)
        else:
            sprop = args.p

    # makes the request to the NIST database
    res = cliQuery(comp=args.c, numOfComp=args.n, year=args.y,
                   author=args.a, keywords=args.k, prop=sprop, verbose=True)

    # show results and ask if to proceed
    printResultTable(res)
    if not args.auto:
        print('\nProceed? [Y]/n  ', end='')
        answ = sys.stdin.readline().strip()
        if answ not in ['', 'y', 'Y']:
            print('Abort by user!')
            exit(1)

    # get full data sets for _all_ references
    dataSets = getAllData(res, verbose=True)

    # write report
    dname = writeReport(dataSets, verbose=True, resDOI=args.doi, reportDir=args.out)
    # print('\nReport written to ' + dname)
    print('pyilt2report finished!')

# Script entry point
if __name__ == "__main__":
    run()