#!/usr/bin/env python
# encoding: utf-8
"""
savcc_normalized_matrix.py

Created by Jorge Herskovic on 2008-04-10.
Copyright (c) 2008 Jorge Herskovic. All rights reserved.
"""

from MEDRank.utility.logger import logging, ULTRADEBUG
import struct
import hashlib
import StringIO
import os.path
from MEDRank.evaluation.savcc_matrix import SavccMatrix
from MEDRank.utility import cache
try:
    from multiprocessing import Lock
except ImportError:
    from threading import Lock
    
_normfactor_lock=Lock()

class SavccNormalizedMatrix(SavccMatrix):
    """SAVCC matrix that adds normalization to the mix. Picklable."""
    def __init__(self, fileobject, transform_function):
        SavccMatrix.__init__(self, fileobject, transform_function)
        # Add normalization factors
        logging.log(ULTRADEBUG, "Initializing normalization array")
        # Default behavior: no normalization
        self.normfactors=[1.0]*self._height
        # Tentative normalization array name
        array_filename=self._expected_norm_array_name()
        logging.debug("Trying to load a normalization array from disk. The "
                      "file should be named %s.", array_filename)
        # Make sure that only one process or thread at a time can attempt to get 
        # the normalization factors
        _normfactor_lock.acquire()
        try:
            try:
                self._load_normalization_factors(open(array_filename, 'rb'))
                logging.debug('Normalization factors loaded from disk.')
            except IOError:
                logging.debug("Unable to load normalization factors from disk.")
                self._generate_normalization_factors()
                # Only save normalization factors if they are not a StringIO
                # object
                if not isinstance(fileobject, StringIO.StringIO):
                    logging.debug("Saving normalization factors to %s",
                                  array_filename)
                    try:
                        self._save_normalization_factors(open(array_filename,
                                                              'wb'))
                    except IOError:
                        logging.warn("Unable to save the normalization array. "
                                     "It will have to be regenerated each "
                                     "time.")
        finally:
            _normfactor_lock.release()
    def __getstate__(self):
        return {'base': SavccMatrix.__getstate__(self),
                'normfact': self.normfactors}
    def __setstate__(self, state):
        SavccMatrix.__setstate__(self, state['base'])
        self.normfactors=state['normfact']
    def _expected_norm_array_name(self):
        """Returns the name that an accumulation array should have, if it
        exists in the file system. This is based on the original filename and
        a hash of the transformation matrix."""
        transform_string=''.join([struct.pack('<d', x) 
                                  for x in self.transform])
        the_hash=hashlib.md5(transform_string).hexdigest()
        return os.path.join(cache.path(), 
                            '%s.%s' % (os.path.basename(self._matrix_file.name),
                                       the_hash))
        
    def _load_normalization_factors(self, load_from):
        """Loads an array of normalization factors from disk."""
        number_size=struct.calcsize('<d')
        counter=0
        number=load_from.read(number_size)
        while number != '':
            self.normfactors[counter]=struct.unpack('<d', number)[0]
            counter+=1
            number=load_from.read(number_size)
        # Make sure it loaded everything correctly! Otherwise, it's time to
        # regenerate
        if counter!=self._height:
            raise IOError("The normalization factor file was not the correct "
            "size for the matrix.")
        return
        
    def _generate_normalization_factors(self):
        """Computes the array of normalization factors for the current 
        matrix."""
        import operator
        logging.info("Generating array of normalization factors. This is a "
                     "slow operation. Please wait.")
        for i in xrange(self._height):
            logging.debug("Generating normalization factor for row %d", i)
            # Add all of the elements of the row together
            matrix_row=self._get_row(i)
            logging.log(ULTRADEBUG, "Row %d contains: %s", i, matrix_row)
            this_row=reduce(operator.add, matrix_row)
            
            if this_row==0.0:
                logging.info("Row %d in the matrix adds up to 0. This may "
                "be a problem, depending on your evaluation function. Since "
                "this is a normalization calculation, it will be replaced by "
                "1.", i)
                this_row=1.0
            self.normfactors[i]=this_row
            logging.log(ULTRADEBUG, "Normalization factor for row %d=%1.5f", i,
                          this_row)
        logging.info("Normalization factor generation done.")
        
    def _save_normalization_factors(self, save_to):
        """Writes the array of normalization factors to a file object in a 
        binary format."""
        assert self._height==len(self.normfactors)
        for i in xrange(self._height):
            save_to.write(struct.pack('<d', self.normfactors[i]))
        return
        
    def __getitem__(self, key):
        i, j=key
        value=self._get_value(i, j)
        factor=self.normfactors[i]
        result=value/factor
        #logging.debug("Getting (%d,%d). Value=%1.5f, normfactor=%1.5f, "
        #              "result=%1.7f", i, j, value, factor, result)
        return result
