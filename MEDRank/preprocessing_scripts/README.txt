Monday, May 12, 2008

The scripts contained in this directory are not terribly elegant or well-written. They are mostly written to massage data from the original UMLS format to something that'll be useful to MEDRank. 

Most of the code is copied from MEDRank v1 and, as such, is ugly but gets the job done. I have tightened it in a very important sense, though: it now fails instead of trying to "fix" the problems behind the scenes. This means that if a parser can't understand it's input data, it'll throw an exception and fail loudly. So, in practical terms, they will do exactly what's expected of them, with no strange side effects.

Despite the ugly code, this should help improve the quality of the data.


